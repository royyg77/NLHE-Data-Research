"""
pipeline/studies/postflop/flop_cbet/study.py

Flop continuation-betting strategy in single-raised pots (SRPs): how c-bet
frequency and bet-size selection vary by board texture and position.

One SQL source (cbet_strategy.sql). The SQL emits one row per
bb_size x player_bucket (HU/MW) x relative_position (IP/OOP) x texture, with
c-bet counts and size-bucket proportions (conditional on a c-bet). The study
shapes that into analysis-ready tables (logic lifted from the v1_0 notebook,
cells 24-26). Plotting lives in plots.py.
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


class FlopCbetStudy(Study):
    name = "flop-cbet"
    category = "Postflop"
    description = "Flop c-bet frequency and size selection by board texture (SRP, v1.0)"

    params = ["stake"]

    outputs = {
        # raw per-(player_bucket, position, texture) rows straight from SQL
        "strategy_raw":    {"sql": "cbet_strategy.sql", "params": ["stake"]},
        # cell 25: aggregated by bb_size / position / texture (HU+MW pooled)
        "strategy_agg":    {"sql": "cbet_strategy.sql", "params": ["stake"]},
        # cell 26 prep: strategy_agg + Wilson CIs on the c-bet frequency
        "strategy_agg_ci": {"sql": "cbet_strategy.sql", "params": ["stake"]},
    }

    # ------------------------------------------------------------------
    # shared SQL runner
    # ------------------------------------------------------------------
    def _raw(self, stake_input):
        params = resolve_stakes(stake_input)
        sql_path = self.sql_dir() / "cbet_strategy.sql"
        return run_sql_file(str(sql_path), params)

    def run(self, output_name, params, min_hands=10000):
        raw = self._raw(params)

        if output_name == "strategy_raw":
            return self._strategy_raw(raw)
        if output_name == "strategy_agg":
            return self._strategy_agg(raw)
        if output_name == "strategy_agg_ci":
            return self._strategy_agg_ci(raw)
        raise ValueError(f"unknown output '{output_name}'")

    # ------------------------------------------------------------------
    # raw view  (light typing only)
    # ------------------------------------------------------------------
    def _strategy_raw(self, df):
        return df.reset_index(drop=True)

    # ------------------------------------------------------------------
    # cell 25: aggregated strategy table
    #   - pools HU/MW (group drops player_bucket)
    #   - rebuilds size counts from per-row pct * cbets, re-derives pcts
    # ------------------------------------------------------------------
    def _strategy_agg(self, df):
        d = df.copy()
        d["texture"] = d["pairedness"] + " | " + d["suitedness"]

        agg = (
            d.assign(
                small_count=d["small_pct"] * d["cbets"],
                medium_count=d["medium_pct"] * d["cbets"],
                large_count=d["large_pct"] * d["cbets"],
                overbet_count=d["overbet_pct"] * d["cbets"],
            )
            .groupby(["bb_size", "relative_position", "texture"], as_index=False)
            .agg(
                cbet_opportunities=("cbet_opportunities", "sum"),
                cbets=("cbets", "sum"),
                small_count=("small_count", "sum"),
                medium_count=("medium_count", "sum"),
                large_count=("large_count", "sum"),
                overbet_count=("overbet_count", "sum"),
            )
        )

        agg["cbet_frequency"] = (agg["cbets"] / agg["cbet_opportunities"] * 100).round(2)
        for bucket in ["small", "medium", "large", "overbet"]:
            agg[f"{bucket}_pct"] = (agg[f"{bucket}_count"] / agg["cbets"] * 100).round(2)

        count_cols = ["small_count", "medium_count", "large_count", "overbet_count"]
        agg[count_cols] = agg[count_cols].round(0).astype(int)

        ordered_cols = [
            "bb_size", "relative_position", "texture",
            "cbet_opportunities", "cbets", "cbet_frequency",
            "small_count", "medium_count", "large_count", "overbet_count",
            "small_pct", "medium_pct", "large_pct", "overbet_pct",
        ]
        return (
            agg[ordered_cols]
            .sort_values(["bb_size", "texture", "relative_position"])
            .reset_index(drop=True)
        )

    # ------------------------------------------------------------------
    # cell 26 prep: strategy_agg + Wilson CIs on the c-bet frequency
    #   CIs computed on the proportion cbets / cbet_opportunities, then
    #   expressed in pct points so they line up with cbet_frequency.
    # ------------------------------------------------------------------
    def _strategy_agg_ci(self, df):
        agg = self._strategy_agg(df)
        agg[["cbet_ci_low", "cbet_ci_high"]] = agg.apply(
            lambda r: pd.Series(_wilson_ci(r["cbets"], r["cbet_opportunities"])),
            axis=1,
        )
        agg["cbet_ci_low_pct"] = agg["cbet_ci_low"] * 100
        agg["cbet_ci_high_pct"] = agg["cbet_ci_high"] * 100
        return agg
    
