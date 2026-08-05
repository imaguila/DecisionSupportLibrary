"""
Efficiency Lens Module.

Ranks candidate solutions based on benefit-cost trade-offs using raw ratios,
min-max normalized efficiency, composite cost aggregation, or Euclidean distance
to ideal target states in objective space.
"""

import logging
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
import pandas as pd

from .base import BaseLens

logger = logging.getLogger(__name__)

EPS: float = 1e-9


class EfficiencyLens(BaseLens):
    """
    Analytical lens for evaluating multi-objective benefit-cost efficiency.

    Provides raw ratio, normalized ratio, multi-cost composite ratio, and
    distance-to-ideal target ranking engines.
    """

    def _normalize_series(self, series: pd.Series) -> pd.Series:
        """Min-Max normalizes a numeric pandas Series to range [0.0, 1.0]."""
        min_v = series.min()
        max_v = series.max()

        if pd.isna(min_v) or pd.isna(max_v) or max_v <= min_v:
            return pd.Series(0.0, index=series.index)

        return (series - min_v) / (max_v - min_v)

    def _resolve_cost_metrics(
        self, df: pd.DataFrame, benefit_col: str, cost_cols: Union[str, Sequence[str]]
    ) -> List[str]:
        """Resolves and validates cost metric column names present in the DataFrame."""
        if isinstance(cost_cols, str):
            raw_costs = [cost_cols]
        else:
            raw_costs = list(cost_cols)

        valid_costs = [
            c
            for c in raw_costs
            if c in df.columns
            and c != benefit_col
            and pd.api.types.is_numeric_dtype(df[c])
        ]
        return valid_costs

    def evaluate(
        self,
        df: pd.DataFrame,
        benefit_col: str,
        cost_cols: Union[str, Sequence[str]],
        method: str = "Benefit/Cost Ratio",
        top_n: Optional[int] = None,
        id_col: str = "id",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Calculates efficiency scores, ranks solutions, and returns an enriched DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            Input solution space DataFrame.
        benefit_col : str
            Name of the column acting as benefit (maximization metric).
        cost_cols : Union[str, Sequence[str]]
            Name(s) of the column(s) acting as cost (minimization metric).
        method : str, default="Benefit/Cost Ratio"
            Efficiency method: "Benefit/Cost Ratio", "Normalized Ratio",
            "Distance to Ideal", or "Composite Cost Ratio".
        top_n : Optional[int], optional
            Maximum number of top solutions to return.
        id_col : str, default="id"
            Unique identifier column name.

        Returns
        -------
        pd.DataFrame
            Ranked DataFrame enriched with 'efficiency_score' and 'efficiency_rank'.
        """
        if df.empty or benefit_col not in df.columns:
            logger.warning("[%s] Empty DataFrame or missing benefit metric.", self.__class__.__name__)
            return pd.DataFrame()

        if not pd.api.types.is_numeric_dtype(df[benefit_col]):
            logger.warning("[%s] Benefit column must be numeric.", self.__class__.__name__)
            return pd.DataFrame()

        valid_costs = self._resolve_cost_metrics(df, benefit_col, cost_cols)
        if not valid_costs:
            logger.warning("[%s] No valid numeric cost columns specified.", self.__class__.__name__)
            return pd.DataFrame()

        result = df.copy()

        # Engine calculations
        normalized_method = method.strip().lower()

        if normalized_method in ["benefit/cost ratio", "raw_ratio", "benefit_cost"]:
            cost_metric = valid_costs[0]
            safe_cost = result[cost_metric].replace(0, EPS)
            score = result[benefit_col] / safe_cost

        elif normalized_method in ["normalized ratio", "normalized_ratio"]:
            cost_metric = valid_costs[0]
            benefit_norm = self._normalize_series(result[benefit_col])
            cost_norm = self._normalize_series(result[cost_metric])
            score = benefit_norm / (cost_norm + EPS)

        elif normalized_method in ["distance to ideal", "distance_to_ideal"]:
            cost_metric = valid_costs[0]
            benefit_norm = self._normalize_series(result[benefit_col])
            cost_norm = self._normalize_series(result[cost_metric])
            distance = ((1.0 - benefit_norm) ** 2 + (cost_norm) ** 2) ** 0.5
            max_distance = 2.0 ** 0.5
            score = 1.0 - (distance / max_distance)

        elif normalized_method in ["composite cost ratio", "composite_cost"]:
            benefit_norm = self._normalize_series(result[benefit_col])
            composite = pd.Series(0.0, index=result.index)
            for c_col in valid_costs:
                composite += self._normalize_series(result[c_col])
            composite /= len(valid_costs)
            score = benefit_norm / (composite + EPS)
            result["efficiency_costs"] = ", ".join(valid_costs)

        else:
            logger.error("[%s] Unrecognized efficiency method: %s", self.__class__.__name__, method)
            return pd.DataFrame()

        result["efficiency_score"] = score
        result = result.sort_values("efficiency_score", ascending=False).copy()
        result["efficiency_rank"] = range(1, len(result) + 1)
        result["efficiency_method"] = method
        result["efficiency_benefit"] = benefit_col
        result["efficiency_primary_cost"] = valid_costs[0]

        if top_n is not None and top_n > 0:
            result = result.head(top_n)

        return result

    def run(
        self,
        df: pd.DataFrame,
        benefit_col: str,
        cost_cols: Union[str, Sequence[str]],
        method: str = "Benefit/Cost Ratio",
        top_n: Optional[int] = 5,
        id_col: str = "id",
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        """
        Runs efficiency scoring and returns a standardized group mapping.

        Returns
        -------
        Dict[str, List[Any]]
            Mapping with group key (e.g., 'Top 5 Efficient (Normalized Ratio)') and matching IDs.
        """
        evaluated_df = self.evaluate(
            df=df,
            benefit_col=benefit_col,
            cost_cols=cost_cols,
            method=method,
            top_n=top_n,
            id_col=id_col,
            **kwargs,
        )

        if evaluated_df.empty:
            return {}

        solution_ids = (
            evaluated_df[id_col].tolist()
            if id_col in evaluated_df.columns
            else evaluated_df.index.tolist()
        )

        n_count = len(solution_ids)
        group_key = f"Top {n_count} Efficient ({method})"
        return {group_key: solution_ids}