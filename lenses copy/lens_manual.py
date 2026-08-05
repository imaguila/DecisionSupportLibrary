"""
Manual Selection Lens Module (lenses/manual.py)

Enables manual filtering and isolation of specific candidate solutions from 
the active solution space using explicit identifier selection.
"""

import logging
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from lenses.base import BaseLens

logger = logging.getLogger(__name__)


class ManualSelectionLens(BaseLens):
    name = "manual"
    category = "manual"

    def render_params(
        self, dataset: Dict[str, Any], working_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Renders Streamlit UI controls for picking candidate solutions by ID.

        Parameters
        ----------
        dataset : Dict[str, Any]
            Global dataset configuration metadata.
        working_df : pd.DataFrame
            Current working solution space DataFrame.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing selected manual solution identifiers.
        """
        params: Dict[str, Any] = {"method": "Manual Selection"}

        if (
            working_df is None
            or working_df.empty
            or "id" not in working_df.columns
        ):
            st.warning("No solutions available for manual selection.")
            params["selected_ids"] = []
            return params

        valid_ids: List[int] = working_df["id"].dropna().astype(int).tolist()

        params["selected_ids"] = st.multiselect(
            "Pick solutions one by one",
            options=valid_ids,
            default=[],
            key="manual_lens_selected_ids",
            help="Manually pick the exact solutions you want to isolate.",
        )

        return params

    def apply(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
        dataset: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Filters the DataFrame to retain only manually selected solution IDs.

        Parameters
        ----------
        df : pd.DataFrame
            Input working solution space DataFrame.
        params : Dict[str, Any]
            Manual selection parameters containing target IDs.
        dataset : Optional[Dict[str, Any]]
            Global context dataset metadata.

        Returns
        -------
        pd.DataFrame
            Filtered DataFrame containing only selected solution records.
        """
        if df is None or df.empty:
            return df

        selected_ids: List[int] = params.get("selected_ids", [])

        if not selected_ids:
            # Return an empty DataFrame with preserved schema if no selection is made
            return df.iloc[0:0].copy()

        return df[df["id"].isin(selected_ids)].copy()

    def render_feedback(self, lens_df: Optional[pd.DataFrame]) -> None:
        """
        Displays UI summary indicators when the manual selection lens is active.

        Parameters
        ----------
        lens_df : Optional[pd.DataFrame]
            Filtered output DataFrame containing active manual selection.
        """
        if lens_df is None:
            return

        count = len(lens_df)
        if count == 0:
            st.caption("No solutions selected in manual lens.")
        else:
            st.info(f"📌 Manual selection: {count} solution(s) active.")


# Alias for backward compatibility
ManualLens = ManualSelectionLens