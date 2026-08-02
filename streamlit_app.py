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

from core.lenses import (
    render_lenses
)
from core.lens_engine import (
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
# FRAMING
# ============================================

filtered_df = apply_framing(
    dataset
)

# ============================================
# WORKSPACE
# ============================================

render_workspace(
    filtered_df,
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

