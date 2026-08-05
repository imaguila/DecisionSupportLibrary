"""
Indicator Lens Module.

Provides multi-criteria selection methods based on domain indicators:
1. Top-N Matches: Aggregates top solutions across individual target dimensions.
2. Non-Dominated Sorting: Identifies Pareto-optimal solutions within the enriched 
   indicator space.
"""

import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from .base import BaseLens

logger = logging.getLogger(__name__)


class IndicatorLens(BaseLens):
    """
    Analytical lens for indicator-driven multi-criteria evaluation and filtering.

    Provides Top-N cross-dimensional match counting and Pareto non-dominated
    sorting engines.
    """

    def _sanitize_criteria(
        self,
        df: pd.DataFrame,
        maximize: Optional[Sequence[str]] = None,
        minimize: Optional[Sequence[str]] = None,
    ) -> Tuple[List[str], List[str], List[str]]:
        """Validates criteria existence and numeric type within the DataFrame."""
        max_cols = list(maximize) if maximize else []
        min_cols = list(minimize) if minimize else []

        valid_max = [
            c
            for c in max_cols
            if c in df.columns and pd.api.types.is_numeric_dtype(df[c])
        ]
        valid_min = [
            c
            for c in min_cols
            if c in df.columns
            and c not in valid_max
            and pd.api.types.is_numeric_dtype(df[c])
        ]

        criteria = valid_max + valid_min
        return valid_max, valid_min, criteria

    def _apply_top_n_matches(
        self,
        df: pd.DataFrame,
        maximize: List[str],
        minimize: List[str],
        top_n: int,
        id_col: str = "id",
    ) -> pd.DataFrame:
        """Computes Top-N match counts per solution across selected criteria."""
        result = df.copy()
        effective_top_n = max(1, min(top_n, len(result)))
        ranked_subsets: List[pd.DataFrame] = []

        solution_id_series = (
            result[id_col] if id_col in result.columns else result.index.to_series()
        )

        for metric in maximize:
            sub = (
                result.sort_values(metric, ascending=False)
                .head(effective_top_n)
                .copy()
            )
            sub_ids = sub[id_col] if id_col in sub.columns else sub.index
            subset_df = pd.DataFrame(
                {
                    "target_id": sub_ids,
                    "matched_metric": metric,
                    "goal": "Maximize",
                }
            )
            ranked_subsets.append(subset_df)

        for metric in minimize:
            sub = (
                result.sort_values(metric, ascending=True)
                .head(effective_top_n)
                .copy()
            )
            sub_ids = sub[id_col] if id_col in sub.columns else sub.index
            subset_df = pd.DataFrame(
                {
                    "target_id": sub_ids,
                    "matched_metric": metric,
                    "goal": "Minimize",
                }
            )
            ranked_subsets.append(subset_df)

        if not ranked_subsets:
            return pd.DataFrame()

        matches = pd.concat(ranked_subsets, ignore_index=True)

        counts = (
            matches.groupby("target_id")
            .size()
            .reset_index(name="domain_match_count")
        )

        matched_metrics = (
            matches.groupby("target_id")["matched_metric"]
            .apply(lambda vals: ", ".join(sorted(set(vals))))
            .reset_index(name="domain_matched_metrics")
        )

        join_key = id_col if id_col in result.columns else result.index.name or "index"
        if id_col not in result.columns:
            result = result.reset_index()

        result = result.merge(
            counts, left_on=join_key, right_on="target_id", how="left"
        ).merge(
            matched_metrics, left_on=join_key, right_on="target_id", how="left"
        )

        if "target_id_x" in result.columns:
            result.drop(columns=["target_id_x", "target_id_y"], inplace=True)
        elif "target_id" in result.columns and target_id != join_key:
            result.drop(columns=["target_id"], inplace=True)

        result["domain_match_count"] = (
            result["domain_match_count"].fillna(0).astype(int)
        )
        result["domain_matched_metrics"] = result[
            "domain_matched_metrics"
        ].fillna("")

        result = result[result["domain_match_count"] > 0].copy()
        if result.empty:
            return result

        result = result.sort_values(
            ["domain_match_count", join_key], ascending=[False, True]
        ).copy()

        result["domain_rank"] = range(1, len(result) + 1)
        result["indicator_method"] = "Top-N Matches"
        result["indicator_top_n"] = effective_top_n

        return result

    def _apply_non_dominated(
        self,
        df: pd.DataFrame,
        maximize: List[str],
        minimize: List[str],
        id_col: str = "id",
    ) -> pd.DataFrame:
        """Filters solutions to retain strictly Pareto non-dominated candidates."""
        result = df.copy()
        criteria = maximize + minimize

        work = result[criteria].copy()

        # Invert minimization dimensions to align strictly as a maximization problem
        for metric in minimize:
            work[metric] = -work[metric]

        values = work.to_numpy()
        n_samples = len(values)
        is_nondominated = np.ones(n_samples, dtype=bool)

        # Pairwise non-dominance evaluation
        for i in range(n_samples):
            current = values[i]
            for j in range(n_samples):
                if i == j:
                    continue
                challenger = values[j]

                # Dominance check: challenger >= current in all & > in at least one
                if np.all(challenger >= current) and np.any(challenger > current):
                    is_nondominated[i] = False
                    break

        result["indicator_nondominated"] = is_nondominated
        result = result[result["indicator_nondominated"]].copy()

        if result.empty:
            return result

        result["indicator_method"] = "Non-dominated"
        result["domain_match_count"] = len(criteria)
        result["domain_matched_metrics"] = ", ".join(criteria)

        sort_key = id_col if id_col in result.columns else result.index
        result = result.sort_values(sort_key, ascending=True).copy()
        result["domain_rank"] = range(1, len(result) + 1)

        return result

    def evaluate(
        self,
        df: pd.DataFrame,
        maximize: Optional[Sequence[str]] = None,
        minimize: Optional[Sequence[str]] = None,
        method: str = "Top-N Matches",
        top_n: int = 5,
        id_col: str = "id",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Calculates multi-criteria indicator matches or non-dominated status.

        Parameters
        ----------
        df : pd.DataFrame
            Input working solution space DataFrame.
        maximize : Optional[Sequence[str]], optional
            List of metrics/indicators to maximize.
        minimize : Optional[Sequence[str]], optional
            List of metrics/indicators to minimize.
        method : str, default="Top-N Matches"
            Method key: "Top-N Matches" or "Non-dominated".
        top_n : int, default=5
            Cut-off per metric when using "Top-N Matches".
        id_col : str, default="id"
            Column name containing unique solution identifiers.

        Returns
        -------
        pd.DataFrame
            Enriched DataFrame filtered to matching solutions.
        """
        if df.empty:
            return pd.DataFrame()

        valid_max, valid_min, criteria = self._sanitize_criteria(
            df, maximize=maximize, minimize=minimize
        )

        if not criteria:
            logger.warning("[%s] No valid numeric criteria provided.", self.__class__.__name__)
            return pd.DataFrame()

        normalized_method = method.strip().lower()

        if normalized_method in ["top-n matches", "top_n", "topn"]:
            return self._apply_top_n_matches(
                df, valid_max, valid_min, top_n=top_n, id_col=id_col
            )
        elif normalized_method in ["non-dominated", "nondominated", "pareto"]:
            return self._apply_non_dominated(
                df, valid_max, valid_min, id_col=id_col
            )
        else:
            logger.error("[%s] Unrecognized indicator method: %s", self.__class__.__name__, method)
            return pd.DataFrame()

    def run(
        self,
        df: pd.DataFrame,
        maximize: Optional[Sequence[str]] = None,
        minimize: Optional[Sequence[str]] = None,
        method: str = "Top-N Matches",
        top_n: int = 5,
        id_col: str = "id",
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        """
        Runs indicator evaluation and groups resulting solution IDs.

        Returns
        -------
        Dict[str, List[Any]]
            Mapping containing match count or Pareto group keys and solution IDs.
        """
        evaluated_df = self.evaluate(
            df=df,
            maximize=maximize,
            minimize=minimize,
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

        groups: Dict[str, List[Any]] = {}

        if "domain_match_count" in evaluated_df.columns and method == "Top-N Matches":
            # Group solutions by number of matched dimensions
            for match_count in sorted(evaluated_df["domain_match_count"].unique(), reverse=True):
                sub_df = evaluated_df[evaluated_df["domain_match_count"] == match_count]
                sub_ids = (
                    sub_df[id_col].tolist()
                    if id_col in sub_df.columns
                    else sub_df.index.tolist()
                )
                group_key = f"Matches = {match_count} (N={len(sub_ids)})"
                groups[group_key] = sub_ids
        else:
            group_key = f"Non-dominated Pareto Front (N={len(solution_ids)})"
            groups[group_key] = solution_ids

        return groups