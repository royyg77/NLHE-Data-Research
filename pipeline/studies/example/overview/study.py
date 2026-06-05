"""
pipeline/studies/example/study.py

Example study covering two SQL sources:
  - texture_frequency.sql  -> board-texture prevalence tables
  - pool_overview.sql      -> analyzed-pool context tables

Each named output returns an analysis-ready DataFrame (logic lifted from
the v1_0 notebook). Plotting lives in plots.py.
"""

import numpy as np
import pandas as pd

from pipeline.core.base import Study
from pipeline.core.runner import run_sql_file, resolve_stakes



def _wilson_ci(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = z * np.sqrt((p * (1 - p) / n) + (z**2 / (4 * n**2))) / denom
    return center - margin, center + margin


class ExampleStudy(Study):
    name = "overview"
    category = "example"
    description = "Analyzed-pool context + flop board-texture prevalence (v1.0)"

    params = ["stake", "min_hands"]

    # output-name -> which SQL file + which params that output consumes
    outputs = {
        # pool_overview.sql
        "pool_all":          {"sql": "pool_overview.sql", "params": ["stake", "min_hands"]},
        "pool_breakdown":    {"sql": "pool_overview.sql", "params": ["stake", "min_hands"]},
        "pool_display":      {"sql": "pool_overview.sql", "params": ["stake", "min_hands"]},
        # texture_frequency.sql
        "texture_by_stake":  {"sql": "texture_frequency.sql", "params": ["stake"]},
        "texture_aggregated":{"sql": "texture_frequency.sql", "params": ["stake"]},
        "texture_pooled_ci": {"sql": "texture_frequency.sql", "params": ["stake"]},
    }

    # ------------------------------------------------------------------
    # shared SQL runner: builds params per-output, runs the file once
    # ------------------------------------------------------------------
    def _raw(self, output_name, stake_input, min_hands):
        spec = self.outputs[output_name]
        sql_params = resolve_stakes(stake_input)
        if "min_hands" in spec["params"]:
            sql_params["min_hands"] = min_hands
        sql_path = self.sql_dir() / spec["sql"]
        return run_sql_file(str(sql_path), sql_params)

    def run(self, output_name, params, min_hands=10000):
        """Execute one named output and return its DataFrame.

        Matches the base Study contract's (output_name, params) shape:
          - params: the stake input -- "all", a single stake like "0.02",
            or a list like ["0.02", "0.05", "0.10"]. Passed to resolve_stakes.
          - min_hands: optional, only consumed by outputs that declare it.
        """
        raw = self._raw(output_name, params, min_hands)

        if output_name == "pool_all":
            return self._pool_all(raw)
        if output_name == "pool_breakdown":
            return self._pool_breakdown(raw)
        if output_name == "texture_by_stake":
            return self._texture_by_stake(raw)
        if output_name == "texture_aggregated":
            return self._texture_aggregated(raw)
        if output_name == "texture_pooled_ci":
            return self._texture_pooled_ci(raw)
        if output_name == "pool_display":
            return self._pool_display_all(raw)
        raise ValueError(f"unknown output '{output_name}'")

    # ------------------------------------------------------------------
    # pool_overview tables  (notebook cells 11, 12, 13)
    # ------------------------------------------------------------------
    def _pool_display(self, df):
        out = df.copy()
        pct_cols = ["pct_hands_see_flop", "pct_flop_hu", "pct_flop_mw"]
        for col in pct_cols:
            out[col] = (out[col] * 100).round(2)
        return out

    def _pool_all(self, df):
        # cell 12: just the "All" preflop-action rows
        disp = self._pool_display(df)
        return disp[disp["pf_action"] == "All"].reset_index(drop=True)

    def _pool_breakdown(self, df):
        # cell 13: SRP / 3BP / 4BP+ rows, ordered
        pf_order = {"SRP": 0, "3BP": 1, "4BP+": 2}
        disp = self._pool_display(df)
        return (
            disp[disp["pf_action"] != "All"]
            .assign(pf_sort=lambda d: d["pf_action"].map(pf_order))
            .sort_values(["pf_sort", "bb_size"])
            .drop(columns="pf_sort")
            .reset_index(drop=True)
        )
    
    def _pool_display_all(self, df):
        # full display frame, all pf_action rows (for the pool plots)
        return self._pool_display(df).reset_index(drop=True)

    # ------------------------------------------------------------------
    # texture_frequency tables  (notebook cells 21, 22, 24)
    # ------------------------------------------------------------------
    def _texture_by_stake(self, df):
        paired_order = {"Unpaired": 0, "Paired": 1, "Trips": 2}
        suited_order = {"Rainbow": 0, "Two-Tone": 1, "Monotone": 2}
        players_order = {"HU": 0, "MW": 1}
        out = df.copy()
        out["texture_frequency"] = (out["texture_frequency"] * 100).round(2)
        return (
            out.assign(
                paired_sort=lambda d: d["pairedness"].map(paired_order),
                suited_sort=lambda d: d["suitedness"].map(suited_order),
                players_sort=lambda d: d["num_players"].map(players_order),
            )
            .sort_values(["bb_size", "players_sort", "paired_sort", "suited_sort"])
            .drop(columns=["paired_sort", "suited_sort", "players_sort"])
            .reset_index(drop=True)
        )

    def _texture_aggregated(self, df):
        out = (
            df.groupby(["bb_size", "pairedness", "suitedness"], as_index=False)["occurrences"]
            .sum()
        )
        out["total_flops"] = out.groupby("bb_size")["occurrences"].transform("sum")
        out["texture_frequency"] = out["occurrences"] / out["total_flops"]
        return out

    def _texture_pooled_ci(self, df):
        out = (
            df.groupby(["pairedness", "suitedness"], as_index=False)["occurrences"]
            .sum()
        )
        out["total_flops"] = out["occurrences"].sum()
        out["texture_frequency"] = out["occurrences"] / out["total_flops"]
        out[["ci_low", "ci_high"]] = out.apply(
            lambda r: pd.Series(_wilson_ci(r["occurrences"], r["total_flops"])),
            axis=1,
        )
        out["freq_pct"] = out["texture_frequency"] * 100
        out["ci_low_pct"] = out["ci_low"] * 100
        out["ci_high_pct"] = out["ci_high"] * 100
        return out.sort_values("texture_frequency", ascending=False).reset_index(drop=True)