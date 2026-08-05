"""
Lens Panel UI Component (ui/lens_panel.py)

Renders sidebar UI controls for dynamic lens selection and parameter collection
within the Streamlit architecture.
"""

import logging
from typing import Any, Dict, Tuple

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

# Clean import from the unified lenses package
from lenses import get_lens, list_lenses

logger = logging.getLogger(__name__)

# Optional mapping for human-readable names in the UI
LENS_DISPLAY_NAMES: Dict[str, str] = {
    "none": "None (Exploratory)",
    "indicator": "Indicators & Pareto",
    "efficiency": "Efficiency & Frontier",
    "manual": "Manual Selection",
    "kmedoids": "Diversity - K-Medoids",
    "kmeans": "Diversity - K-Means",
    "agglomerative": "Diversity - Agglomerative",
    "hdbscan": "Diversity - HDBSCAN",
    "weighted_sum": "Preference - Weighted Sum",
    "topsis": "Preference - TOPSIS",
    "vikor": "Preference - VIKOR",
    "reference_point": "Preference - Reference Point",
    "consensus": "SOI Consensus",
}


def render_lens_header(active_lens_key: str) -> None:
    """Renders the visual header and session context indicator for the selected lens."""
    active_soi = st.session_state.get("active_soi_name")
    if active_soi:
        st.caption(f"Working on active SOI: **{active_soi}**")

    if active_lens_key and active_lens_key != "none":
        display_name = LENS_DISPLAY_NAMES.get(active_lens_key, active_lens_key.title())
        st.markdown(
            f"""
            <div style="
                color:#E63946;
                font-size:12px;
                font-weight:600;
                text-align:center;
                margin:0.3rem 0 0.8rem 0;
            ">
                ───── Lens: {display_name} ─────
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_active_lens_params(
    active_lens_key: str, dataset: Dict[str, Any], working_df: pd.DataFrame
) -> Dict[str, Any]:
    """Retrieves and renders UI parameter controls for the selected lens."""
    if not active_lens_key or active_lens_key.lower() == "none":
        return {}

    lens_instance = get_lens(active_lens_key)

    if lens_instance is None:
        st.warning(f"No registered lens found for: '{active_lens_key}'")
        return {}

    # Check if the lens defines its own UI parameter rendering
    if hasattr(lens_instance, "render_params") and callable(
        getattr(lens_instance, "render_params")
    ):
        try:
            return lens_instance.render_params(dataset, working_df)
        except Exception as e:
            logger.error("Error rendering parameters for lens '%s': %s", active_lens_key, str(e))
            st.error(f"Error loading parameters for '{active_lens_key}': {str(e)}")
            return {}

    return {}


def render_lens_panel(
    dataset_config: Dict[str, Any], working_df: pd.DataFrame
) -> Tuple[str, Dict[str, Any], DeltaGenerator, DeltaGenerator]:
    """
    Renders the sidebar panel for lens selection and UI container initialization.

    Parameters
    ----------
    dataset_config : Dict[str, Any]
        Global dataset configuration metadata.
    working_df : pd.DataFrame
        Current working solution space DataFrame.

    Returns
    -------
    Tuple[str, Dict[str, Any], DeltaGenerator, DeltaGenerator]
        - active_lens_key: Selected lens key (e.g. 'topsis', 'none').
        - params: Parameter dictionary collected from the UI.
        - feedback_placeholder: Container for feedback metrics.
        - selection_placeholder: Container for grouping and saving UI.
    """
    params: Dict[str, Any] = {}
    available_keys = ["none"] + list_lenses()

    with st.sidebar.expander("🧭 Solution of Interest Lens", expanded=False):
        selected_key = st.selectbox(
            "Select an analytical lens:",
            options=available_keys,
            format_func=lambda k: LENS_DISPLAY_NAMES.get(k, k.title()),
            key="active_lens_selector",
        )

        render_lens_header(selected_key)

        params = render_active_lens_params(selected_key, dataset_config, working_df)

        feedback_placeholder = st.empty()
        selection_placeholder = st.empty()

    return (
        selected_key,
        params,
        feedback_placeholder,
        selection_placeholder,
    )