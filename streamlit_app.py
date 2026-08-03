## --------------------------------------------------------------------------------------
## streamlit_app.py



import streamlit as st

from ui.input_panel import render_input_panel

from core.enrichment import (
    render_enrichment
)

from core.framing import (
    apply_framing
)

from core.workspace import (
    render_workspace
)

from core.workspace_controls import (
    render_workspace_controls
)

from lenses.lenses import (
    render_lenses
)

from lenses.lens_engine import (
    apply_lens
)


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

    st.info(
        "Select a domain configuration to begin."
    )

    st.stop()

# ==================================================
# ENRICHMENT
# ==================================================

dataset = render_enrichment(
    dataset
)

# ==================================================
# WORKSPACE CONTROLS
# ==================================================

dimensions = (
    dataset["metrics"]
    +
    dataset["selected_indicators"]
)

show_ids = render_workspace_controls(
    dimensions
)


# ==================================================
# SAVE CURRENT SOI
# ==================================================

if (
    "pending_save_soi"
    in st.session_state
):

    if "saved_sois" not in st.session_state:

        st.session_state.saved_sois = []

    pending = (
        st.session_state.pending_save_soi
    )

    existing_names = [
        soi["name"]
        for soi in st.session_state.saved_sois
    ]

    if pending["name"] in existing_names:

        st.sidebar.warning(
            "A SOI with this name already exists."
        )

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

        st.sidebar.success(
            f"Saved SOI: {pending['name']}"
        )

    del st.session_state[
        "pending_save_soi"
    ]

# ==================================================
# LOADED SOI
# ==================================================

view_df = lens_df.copy()

if (
    active_lens == "None"
    and
    "active_soi_ids"
    in st.session_state
):

    view_df = view_df[
        view_df["id"].isin(
            st.session_state.active_soi_ids
        )
    ]

# ==================================================
# WORKSPACE
# ==================================================

render_workspace(
    view_df,
    dataset,
    show_ids
)