"""
Base Lens Module.

Defines the abstract interface that all analytical lenses must implement
to guarantee a consistent return structure across single- and multi-group methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import pandas as pd


class BaseLens(ABC):
    """Abstract base class for all decision-space analytical lenses."""

    @abstractmethod
    def run(
        self,
        df: pd.DataFrame,
        feature_cols: List[str],
        id_col: str = "id",
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        """
        Executes the analytical lens partition algorithm.

        Parameters
        ----------
        df : pd.DataFrame
            Active dataset of Pareto solutions.
        feature_cols : List[str]
            List of column names (objectives, indicators, variables) to analyze.
        id_col : str, default="id"
            Column name containing unique solution identifiers.
        **kwargs : Any
            Lens-specific algorithmic parameters.

        Returns
        -------
        Dict[str, List[Any]]
            Mapping of group labels to lists of selected solution IDs.
        """
        pass