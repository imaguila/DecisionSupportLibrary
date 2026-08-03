## --------------------------------------------------------------------------------------
## streamlit_app.py
## --------------------------------------------------------------------------------------

import streamlit as st

from ui.input_panel import render_input_panel

from core.enrichment import (
    render_enrichment )

from core.framing import (
    apply_framing )

from core.workspace import (
    render_workspace )

from core.workspace_controls import (
    render_workspace_controls )

from lenses.lenses import (
    render_lenses )

from lenses.lens_engine import (
    apply_lens )

st.set_page_config(
    page_title="Decision Space Explorer",
    layout="wide"
)

st.markdown("""
<style>

[data-testid="stExpander"] details summary p {
    font-size: 1.2rem;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)

st.title(
    "Decision Space Explorer"
)

# ==================================================
# INPUT
# ==================================================

dataset = render_input_panel()

if dataset is None:
    st.info( "Select a domain configuration to begin."  )
    st.stop()

# ==================================================
# ENRICHMENT
# ==================================================

dataset = render_enrichment( dataset )

# ==================================================
# WORKSPACE CONTROLS
# ==================================================

dimensions = ( dataset["metrics"] +
    dataset["selected_indicators"]
)

show_ids = render_workspace_controls(
    dimensions
)

# ==================================================
# FRAMING
# ==================================================

framed_df = apply_framing( dataset
)

# ==================================================
# WORKING DATASET
# ==================================================

working_df = framed_df.copy()

if "active_soi_ids" in st.session_state:

    working_df = working_df[
        working_df["id"].isin(
            st.session_state.active_soi_ids
        )
    ].copy()

# ==================================================
# RESET LENS AFTER LOADING SOI
# ==================================================

if st.session_state.get( "pending_lens_reset", False) :
    st.session_state[ "active_lens" ] = "None"
    st.session_state[ "pending_lens_reset" ] = False

# ==================================================
# LENSES / SOI IDENTIFICATION
# ==================================================

active_lens, lens_params, lens_feedback = (  render_lenses( dataset, working_df ) )

lens_df = apply_lens( working_df, active_lens, lens_params, dataset )

# ==================================================
# LENS FEEDBACK
# ==================================================

if lens_feedback is not None:

    with lens_feedback.container():

        if active_lens == "Diversity":

            if "cluster" in lens_df.columns:

                n_clusters = (
                    lens_df["cluster"]
                    .dropna()
                    .astype(int)
                    .loc[
                        lambda s: s != -1
                    ]
                    .nunique()
                )

                st.info(
                    f"Clusters detected: {n_clusters}"
                )

            if "diversity_k" in lens_df.columns:

                k_value = (
                    lens_df["diversity_k"]
                    .dropna()
                    .iloc[0]
                )

                st.success(
                    f"Selected k: {int(k_value)}"
                )

            if "diversity_silhouette" in lens_df.columns:

                silhouette_value = (
                    lens_df["diversity_silhouette"]
                    .dropna()
                    .iloc[0]
                )

                st.caption(
                    f"Silhouette score: {silhouette_value:.3f}"
                )




if lens_df is None:
    st.sidebar.warning(
        "The selected lens returned no dataset. "
        "Reverting to the current working dataset."
    )
    lens_df = working_df.copy()


# ==================================================
# SAVE CURRENT SOI
# ==================================================

if "pending_save_soi" in st.session_state:
    if "saved_sois" not in st.session_state:
        st.session_state.saved_sois = []

    pending = ( st.session_state.pending_save_soi )
    existing_names = [
        soi["name"]
        for soi in st.session_state.saved_sois
    ]

    if pending["name"] in existing_names:
        st.sidebar.warning( "A SOI with this name already exists." )
    else:
        st.session_state.saved_sois.append(
            {
                "name": pending["name"],
                "lens": pending["lens"],
                "params": pending.get(
                    "params",
                    {}
                ),
                "ids": lens_df["id"].tolist()
            }
        )
        st.sidebar.success( f"Saved SOI: {pending['name']}"
        )
    del st.session_state[ "pending_save_soi" ]

# ==================================================
# WORKSPACE
# ==================================================

render_workspace( lens_df, dataset, show_ids )