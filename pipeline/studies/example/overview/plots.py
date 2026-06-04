"""
pipeline/studies/example/plots.py

Study-specific visuals for the example study. Each function takes an
analysis-ready DataFrame (from study.run(...)) and RETURNS Plotly figure(s).
Never calls .show() — the front-end decides how to render, which keeps
dashboard.py generic.

Pool-overview plots expect the RAW pool_overview output (proportions 0-1),
so call study.run with the matching output, OR pass the raw frame. To keep
this simple, these take the same tables the study returns and recompute the
pivots they need.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


PAIRED_ORDER = ["Unpaired", "Paired", "Trips"]
SUITED_ORDER = ["Rainbow", "Two-Tone", "Monotone"]
PF_ORDER = ["All", "SRP", "3BP", "4BP+"]


# ----------------------------------------------------------------------
# texture_frequency heatmaps  (notebook cell 23)
# expects: texture_aggregated output
# ----------------------------------------------------------------------
def texture_heatmaps(df):
    """Returns a list of (label, figure) — one heatmap per stake."""
    figures = []
    for stake in sorted(df["bb_size"].unique()):
        grid = (
            df[df["bb_size"] == stake]
            .pivot(index="pairedness", columns="suitedness", values="texture_frequency")
            .reindex(index=PAIRED_ORDER, columns=SUITED_ORDER)
        )
        fig = px.imshow(
            grid, text_auto=".3f", color_continuous_scale="magma", aspect="auto",
            labels=dict(x="Suitedness", y="Pairedness", color="Frequency"),
            title=f"bb_size = {stake:.2f}",
        )
        fig.update_layout(margin=dict(l=40, r=20, t=50, b=40))
        figures.append((f"bb_size = {stake:.2f}", fig))
    return figures


# ----------------------------------------------------------------------
# pool_overview plots  (notebook cells 14, 15, 16)
# these expect a pool_overview frame that still has ALL pf_action rows.
# pass study.run("pool_breakdown", ...) won't work (it drops "All"); instead
# these recompute from a frame containing every pf_action — see dashboard
# wiring note. For convenience they accept the display frame with pct columns.
# ----------------------------------------------------------------------
def preflop_action_distribution(df):
    """Cell 14: stacked/group bar of pf_action share by stake.
    Expects rows for SRP/3BP/4BP+ with a 'number_hands' column."""
    pf = df[df["pf_action"] != "All"].copy()
    pivot = pf.pivot(index="bb_size", columns="pf_action", values="number_hands")
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
    order = pivot_pct.mean(axis=0).sort_values(ascending=False).index
    pivot_pct = pivot_pct[order]
    fig = px.bar(
        pivot_pct, barmode="group",
        labels=dict(value="frequency (%)", bb_size="bb_size", pf_action="pf_action"),
        title="Preflop Action Distribution by Stake",
    )
    return fig


def flop_seen_rate(df):
    """Cell 15: pct_hands_see_flop by stake and pf_action.
    Expects all pf_action rows with 'pct_hands_see_flop' column."""
    pivot = df.pivot(index="bb_size", columns="pf_action", values="pct_hands_see_flop")
    pivot = pivot[[c for c in PF_ORDER if c in pivot.columns]]
    fig = px.bar(
        pivot, barmode="group",
        labels=dict(value="pct_hands_see_flop", bb_size="bb_size"),
        title="Flop-Seen Rate by Stake and Preflop Action",
    )
    return fig


def flop_hu_vs_mw(df):
    """Cell 16: side-by-side HU vs MW flop rate by stake and pf_action.
    Expects all pf_action rows with 'pct_flop_hu' and 'pct_flop_mw'."""
    cols = [c for c in PF_ORDER if c in df["pf_action"].unique()]
    hu = df.pivot(index="bb_size", columns="pf_action", values="pct_flop_hu")[cols]
    mw = df.pivot(index="bb_size", columns="pf_action", values="pct_flop_mw")[cols]

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Pct Flop HU", "Pct Flop MW"))
    for action in cols:
        fig.add_trace(go.Bar(name=action, x=hu.index.astype(str), y=hu[action]), row=1, col=1)
        fig.add_trace(go.Bar(name=action, x=mw.index.astype(str), y=mw[action],
                             showlegend=False), row=1, col=2)
    fig.update_layout(barmode="group", title_text="Flop HU vs MW Rate by Stake and Preflop Action")
    return fig