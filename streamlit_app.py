import streamlit as st

from ui.input_panel import render_input_panel
from core.framing import apply_framing
from core.workspace import render_workspace

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

from lenses.lenses import (
    render_lenses
)
from lenses.lens_engine import (
    apply_lens
)
from core.enrichment import (
    render_enrichment
)


st.title("Decision Space Explorer")

dataset = render_input_panel()

if dataset is None:

    st.info(
        "Select a domain configuration to begin."
    )
    st.stop()

# ============================================
# ENRICHMENT
# ============================================

dataset = render_enrichment(
    dataset
)

# ============================================
# WORKSPACE
# ============================================

from core.workspace_controls import (
    render_workspace_controls
)

dimensions = (
    dataset["metrics"]
    +
    dataset["selected_indicators"]
)
show_ids = render_workspace_controls(
    dimensions
)

# ============================================
# FRAMING
# ============================================

filtered_df = apply_framing(
    dataset
)

# ============================================
# LENSES
# ============================================

active_lens, lens_params = (
    render_lenses(dataset)
)

filtered_df = apply_lens(
    filtered_df,
    active_lens,
    lens_params,
    dataset
)


# ============================================
# LOADED SOI
# ============================================

if (
    "active_soi_ids"
    in st.session_state
):

    filtered_df = filtered_df[
        filtered_df["id"].isin(
            st.session_state.active_soi_ids
        )
    ]



if (
    "pending_save_soi"
    in st.session_state
):

    pending = (
        st.session_state.pending_save_soi
    )

    st.session_state.saved_sois.append(
        {
            "name": pending["name"],
            "lens": pending["lens"],
            "ids": filtered_df["id"].tolist()
        }
    )

    del st.session_state[
        "pending_save_soi"
    ]
# ============================================
# WORKSPACE
# ============================================

render_workspace(
    filtered_df,
    dataset,
    show_ids
)