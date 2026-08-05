"""
Manual Selection Lens (lenses/manual.py)
"""

from typing import Any, Dict, Optional
import pandas as pd
import streamlit as st

from lenses.base import BaseLens


class ManualLens(BaseLens):
    name = "manual"
    category = "manual"

    def render_params(
        self, dataset: Dict[str, Any], working_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Renders multiselect widget for manual solution picking."""
        all_ids = working_df["id"].tolist() if "id" in working_df.columns else []

        selected_ids = st.multiselect(
            "Select Candidate Solution IDs:",
            options=all_ids,
            default=all_ids[:5] if len(all_ids) >= 5 else all_ids,
            key="manual_lens_ids_selector",
        )
        return {"selected_ids": selected_ids}

    def apply(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
        dataset: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """Filters DataFrame to include only user-selected candidate IDs."""
        selected_ids = params.get("selected_ids", [])
        if not selected_ids:
            return df.copy()

        if "id" in df.columns:
            return df[df["id"].isin(selected_ids)].copy()

        return df.copy()