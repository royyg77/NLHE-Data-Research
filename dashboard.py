"""
dashboard.py — Streamlit front-end.

Same idea as cli.py, but the user picks options with on-screen controls
instead of command-line flags, and results render as tables instead of
printing to the terminal.

Run it with:
    streamlit run dashboard.py

Streamlit's model in one sentence: this whole script re-runs top to bottom
every time the user changes a control. A widget like st.selectbox(...) both
draws the control AND returns whatever the user currently has selected.
"""

import streamlit as st

from pipeline.core.config import default_min_hands
from pipeline.core.runner import available_stakes
from pipeline.registry import get_study, studies_by_category, study_names
from pipeline.core.io import save_results


# --- page setup -------------------------------------------------------------
# Sets the browser tab title and uses the wider layout (good for tables).
st.set_page_config(page_title="NLHE Data Research", layout="wide")
st.title("NLHE Data Research")


# --- 1. pick a study --------------------------------------------------------
# studies_by_category() returns {category: [study, ...]}. We flatten it into a
# {display_name: study_name} map so the dropdown can show readable labels and
# we can recover the real study name from the selection.
study_label_to_name = {}
for category, studies in studies_by_category().items():
    for study in studies:
        study_label_to_name[f"{study.name}  ·  {category}"] = study.name

# st.selectbox draws a dropdown and returns the chosen label.
chosen_label = st.selectbox("Study", list(study_label_to_name))
study_name = study_label_to_name[chosen_label]
study = get_study(study_name)

st.caption(study.description)


# --- 2. pick parameters -----------------------------------------------------
# Put the controls in a sidebar so they sit beside the results, not above them.
with st.sidebar:
    st.header("Parameters")

    # Stake: try to read the real stakes from the DB. If that fails (no DB
    # reachable), fall back to a plain "all" so the page still loads.
    try:
        stakes = [f"{s:.2f}" for s in available_stakes()]
        stake_choices = ["all"] + stakes
    except Exception:
        stake_choices = ["all"]
        st.warning("Could not reach the database to list stakes; defaulting to 'all'.")

    # multiselect lets the user pick several stakes (or none -> we treat as "all").
    selected_stakes = st.multiselect(
        "Stake (bb_size)", stake_choices, default=["all"]
    )

    # Only studies that declare "min_hands" in their params use it. Show the
    # control only for those; otherwise the knob would do nothing.
    if "min_hands" in study.params:
        min_hands = st.number_input(
            "Minimum hands", min_value=0, value=default_min_hands(), step=1000
        )
    else:
        min_hands = default_min_hands()  # passed but ignored by these studies

    # Which outputs to show. Defaults to all of the study's declared outputs.
    selected_outputs = st.multiselect(
        "Outputs", list(study.outputs), default=list(study.outputs)
    )

    save = st.checkbox("Save results to disk", value=False)

    # Nothing runs until this button is clicked.
    run_clicked = st.button("Run study", type="primary")


# --- 3. run and 4. show -----------------------------------------------------
# Turn the stake selection into the shape resolve_stakes expects:
#   - "all" anywhere      -> "all"
#   - one stake           -> that single string
#   - several stakes      -> a list of strings
def stake_input_from_selection(selected):
    if not selected or "all" in selected:
        return "all"
    if len(selected) == 1:
        return selected[0]
    return selected


if run_clicked:
    stake_input = stake_input_from_selection(selected_stakes)

    # A declared plot needs its source output to have been run. Make sure any
    # output required by a plot is included even if the user didn't tick it,
    # so charts always render. Preserves the user's selection order otherwise.
    plot_specs = getattr(study, "plots", {})
    needed_for_plots = {spec["output"] for spec in plot_specs.values()}
    to_run = list(selected_outputs)
    for name in needed_for_plots:
        if name not in to_run and name in study.outputs:
            to_run.append(name)

    outputs = {}
    for name in to_run:
        with st.spinner(f"Running {name}…"):
            df = study.run(name, stake_input, min_hands=min_hands)
        outputs[name] = df

    # --- charts first (if the study declares any) ---------------------------
    # study.plots maps a label -> {"fn": <fig-returning function>, "output": <name>}.
    for label, spec in plot_specs.items():
        needed = spec["output"]
        if needed not in outputs:
            continue
        st.subheader(label)
        fig = spec["fn"](outputs[needed])
        st.plotly_chart(fig, use_container_width=True)

    # --- then the raw tables, tucked into expanders -------------------------
    st.divider()
    st.caption("Underlying data")
    for name, df in outputs.items():
        with st.expander(f"{name}  ({len(df)} rows)"):
            st.dataframe(df, use_container_width=True)

    if save and outputs:
        out_dir = save_results(study.name, outputs)
        st.success(f"Results saved to {out_dir}")
else:
    # Shown before the first run.
    st.info("Set parameters in the sidebar and click **Run study**.")

