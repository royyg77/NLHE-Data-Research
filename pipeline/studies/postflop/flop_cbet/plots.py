"""
pipeline/studies/postflop/flop_cbet/plots.py

Study-specific visuals for the flop c-bet study. Each function takes an
analysis-ready DataFrame (from study.run(...)) and RETURNS a Plotly figure.
Never calls .show() -- the front-end decides how to render.

Ported from notebook cells 26 (c-bet frequency by texture, with Wilson CIs)
and 27 (size mix by texture/position). The notebook drew these with matplotlib;
here they return Plotly figures to match the dashboard's generic plots()
interface.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Fixed texture display order from the notebook (cell 26). Only textures that
# actually appear in the data are drawn, in this order.
TEXTURE_ORDER = [
    "Unpaired | 2Tone",
    "Unpaired | Rainbow",
    "Unpaired | Monotone",
    "Paired | 2Tone",
    "Paired | Rainbow",
    "Trips | Rainbow",
]
POSITIONS = ["IP", "OOP"]
POS_COLORS = {"IP": "#2E86AB", "OOP": "#E63946"}
SIZE_BUCKETS = ["small_pct", "medium_pct", "large_pct", "overbet_pct"]
SIZE_LABELS = {"small_pct": "Small", "medium_pct": "Medium",
               "large_pct": "Large", "overbet_pct": "Overbet"}


def _stakes(df):
    return sorted(df["bb_size"].unique())


def _textures_present(df):
    present = set(df["texture"].unique())
    return [t for t in TEXTURE_ORDER if t in present]


# ----------------------------------------------------------------------
# cell 26: c-bet frequency by texture, IP vs OOP, with Wilson CIs
# expects: strategy_agg_ci output (has cbet_ci_low_pct / cbet_ci_high_pct)
# ----------------------------------------------------------------------
def cbet_frequency_by_texture(df):
    """Grouped bars (IP vs OOP) of c-bet frequency per texture, with Wilson-CI
    error bars; one subplot column per stake. Returns a single Plotly figure."""
    stakes = _stakes(df)
    textures = _textures_present(df)

    fig = make_subplots(
        rows=1, cols=len(stakes),
        shared_yaxes=True,
        subplot_titles=[f"bb_size = {s:.2f}" for s in stakes],
    )

    for col, stake in enumerate(stakes, start=1):
        sub = df[df["bb_size"] == stake]
        for pos in POSITIONS:
            pos_data = (
                sub[sub["relative_position"] == pos]
                .set_index("texture")
                .reindex(textures)
                .reset_index()
            )
            freq = pos_data["cbet_frequency"]
            err_low = freq - pos_data["cbet_ci_low_pct"]
            err_high = pos_data["cbet_ci_high_pct"] - freq
            fig.add_trace(
                go.Bar(
                    name=pos,
                    legendgroup=pos,
                    showlegend=(col == 1),  # one legend entry per position
                    x=textures,
                    y=freq,
                    marker_color=POS_COLORS[pos],
                    error_y=dict(type="data", symmetric=False,
                                 array=err_high, arrayminus=err_low),
                ),
                row=1, col=col,
            )

    fig.update_layout(
        barmode="group",
        title_text="Flop C-bet Frequency by Texture and Position (with 95% Wilson CIs)",
        legend_title="Position",
    )
    fig.update_yaxes(title_text="C-bet frequency (%)", row=1, col=1)
    fig.update_xaxes(tickangle=-45)
    return fig


# ----------------------------------------------------------------------
# cell 27: size mix (stacked) by texture and position
# expects: strategy_agg (or strategy_agg_ci) output with the *_pct columns
# ----------------------------------------------------------------------
def cbet_size_mix(df):
    """Stacked bars of conditional size mix (Small/Medium/Large/Overbet) per
    texture x position; one subplot column per stake. Returns a Plotly figure."""
    stakes = _stakes(df)
    textures = _textures_present(df)

    fig = make_subplots(
        rows=1, cols=len(stakes),
        shared_yaxes=True,
        subplot_titles=[f"bb_size = {s:.2f}" for s in stakes],
    )

    for col, stake in enumerate(stakes, start=1):
        sub = df[df["bb_size"] == stake].copy()
        # order rows by texture (fixed) then position, like the notebook
        sub["tex_rank"] = sub["texture"].map({t: i for i, t in enumerate(textures)})
        sub = (
            sub[sub["texture"].isin(textures)]
            .sort_values(["tex_rank", "relative_position"])
            .reset_index(drop=True)
        )
        labels = [f"{t} / {p}" for t, p in zip(sub["texture"], sub["relative_position"])]

        for bucket in SIZE_BUCKETS:
            fig.add_trace(
                go.Bar(
                    name=SIZE_LABELS[bucket],
                    legendgroup=bucket,
                    showlegend=(col == 1),
                    x=labels,
                    y=sub[bucket],
                ),
                row=1, col=col,
            )

    fig.update_layout(
        barmode="stack",
        title_text="Flop C-bet Size Mix by Texture and Position",
    )
    fig.update_yaxes(title_text="Size mix (%)", row=1, col=1)
    fig.update_xaxes(tickangle=-45)
    return fig

