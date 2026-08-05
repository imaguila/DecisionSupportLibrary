"""
Lens Panel UI Component (ui/lens_panel.py)

Renders sidebar UI controls for categorized analytical lens selection,
dynamic parameter configuration, and container placeholders within the Decision Space Explorer.
"""

import logging
from typing import Any, Dict, Tuple

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from lenses import get_lens

logger = logging.getLogger(__name__)

# Structured Catalog: Categories mapped to Lens Keys and Display Names
LENS_CATALOG: Dict[str, Dict[str, str]] = {
    "🔍 Exploratory": {
        "none": "None (Full Working Dataset)",
    },
    "📊 Indicators & Efficiency": {
        "indicator": "Indicators & Pareto Selection",
        "efficiency": "Efficiency Frontier",
    },
    "🧩 Diversity Analysis": {
        "kmeans": "K-Means Clustering",
        "kmedoids": "K-Medoids Clustering",
        "agglomerative": "Agglomerative Clustering",
        "hdbscan": "HDBSCAN Clustering",
    },
    "⚖️ Preference & MCDM": {
        "weighted_sum": "Weighted Sum Method",
        "topsis": "TOPSIS",
        "vikor": "VIKOR",
        "reference_point": "Reference Point Method",
    },
    "🔀 Meta-Lens": {
        "consensus": "SOI Consensus",
    },
    "🎯 Manual": {
        "manual": "Manual Candidate Selection",
    },
}


def _get_category_and_lens_key(active_lens: str) -> Tuple[str, str]:
    """Retrieves current category and normalized key for active lens."""
    target_key = str(active_lens).lower().strip()
    for category, lenses in LENS_CATALOG.items():
        if target_key in lenses:
            return category, target_key
    return "🔍 Exploratory", "none"


def render_lens_header(lens_display_name: str) -> None:
    """Renders visual header banner for the selected lens."""
    active_soi = st.session_state.get("active_soi_name")
    if active_soi:
        st.caption(f"Working on active SOI: **{active_soi}**")

    st.markdown(
        f"""
        <div style="
            color:#E63946;
            font-size:12px;
            font-weight:600;
            text-align:center;
            margin:0.2rem 0 0.6rem 0;
        ">
            ───── Lens: {lens_display_name} ─────
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_active_lens_params(
    active_lens_key: str, dataset: Dict[str, Any], working_df: pd.DataFrame
) -> Dict[str, Any]:
    """Renders interactive parameter controls for the active lens."""
    if not active_lens_key or active_lens_key == "none":
        return {}

    lens_instance = get_lens(active_lens_key)

    if lens_instance is None:
        st.warning(f"No module registered for lens: '{active_lens_key}'")
        return {}

    if hasattr(lens_instance, "render_params") and callable(getattr(lens_instance, "render_params")):
        try:
            params = lens_instance.render_params(dataset, working_df)
            return params if isinstance(params, dict) else {}
        except Exception as e:
            logger.error("Error rendering parameters for lens '%s': %s", active_lens_key, str(e))
            st.error(f"Error loading parameters for '{active_lens_key}': {str(e)}")
            return {}

    return {}


def render_lens_panel(
    dataset_config: Dict[str, Any], working_df: pd.DataFrame
) -> Tuple[str, Dict[str, Any], DeltaGenerator, DeltaGenerator]:
    """
    Renders sidebar controls grouped by Category and Lens with parameters and placeholders.
    """
    params: Dict[str, Any] = {}

    current_active_lens = st.session_state.get("active_lens", "none")
    default_cat, default_lens_key = _get_category_and_lens_key(current_active_lens)

    category_keys = list(LENS_CATALOG.keys())
    cat_index = category_keys.index(default_cat) if default_cat in category_keys else 0

    with st.sidebar.expander("🧭 Solution of Interest (Lens Selection)", expanded=True):
        # 1. Category Selection
        selected_category = st.selectbox(
            "1. Select Category:",
            options=category_keys,
            index=cat_index,
            key="lens_category_selector",
        )

        # 2. Specific Lens Selection
        available_lenses = LENS_CATALOG[selected_category]
        lens_keys = list(available_lenses.keys())
        lens_index = lens_keys.index(default_lens_key) if default_lens_key in lens_keys else 0

        selected_lens_key = st.selectbox(
            "2. Select Analytical Lens:",
            options=lens_keys,
            index=lens_index,
            format_func=lambda k: available_lenses[k],
            key="active_lens_key_selector",
        )

        # Sync session state
        st.session_state["active_lens"] = selected_lens_key

        # Header
        render_lens_header(available_lenses[selected_lens_key])

        # 3. Dynamic Lens Controls / Parameters
        params = render_active_lens_params(selected_lens_key, dataset_config, working_df)

        # 4. Placeholders for feedback and save controls
        feedback_placeholder = st.empty()
        selection_placeholder = st.empty()

    return (
        selected_lens_key,
        params,
        feedback_placeholder,
        selection_placeholder,
    )