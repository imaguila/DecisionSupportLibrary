"""
Manual Selection Lens Module.

Enables explicit filtering and isolation of specific candidate solutions 
from the solution space based on user-selected unique identifiers.
"""

import logging
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd

from .base import BaseLens

logger = logging.getLogger(__name__)


class ManualSelectionLens(BaseLens):
    """
    Analytical lens for manual candidate solution selection.

    Isolates specific solutions by their unique identifiers without applying
    algorithmic ranking or unsupervised clustering.
    """

    def run(
        self,
        df: pd.DataFrame,
        selected_ids: Optional[Sequence[Any]] = None,
        id_col: str = "id",
        group_name: str = "Manual Selection",
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        """
        Filters input DataFrame to retain only user-selected IDs.

        Parameters
        ----------
        df : pd.DataFrame
            Input working solution space DataFrame.
        selected_ids : Optional[Sequence[Any]], optional
            Collection of solution identifiers chosen for manual isolation.
        id_col : str, default="id"
            Column name containing unique solution identifiers.
        group_name : str, default="Manual Selection"
            Label used for the output grouping dictionary key.

        Returns
        -------
        Dict[str, List[Any]]
            Mapping containing the active group label and matching solution IDs.
        """
        if df.empty or not selected_ids:
            return {}

        # Determine identifier source (explicit column vs index)
        if id_col in df.columns:
            available_ids = set(df[id_col])
        else:
            available_ids = set(df.index)

        # Retain only valid IDs present in the dataset
        valid_selected = [s_id for s_id in selected_ids if s_id in available_ids]

        if not valid_selected:
            logger.warning(
                "[%s] None of the selected IDs exist in the active dataset.",
                self.__class__.__name__,
            )
            return {}

        label = f"{group_name} (N={len(valid_selected)})"
        return {label: valid_selected}