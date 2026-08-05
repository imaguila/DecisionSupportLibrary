"""
Consensus Lens Module.

Aggregates multiple saved Sets of Interest (SOIs) into a unified consensus
model using threshold-based voting logic, unions, majorities, or intersections.
"""

import logging
from typing import Any, Dict, List, Optional, Sequence, Union

import pandas as pd

from .base import BaseLens

logger = logging.getLogger(__name__)


class ConsensusLens(BaseLens):
    """
    Analytical meta-lens for combining multiple saved solution sets (SOIs).

    Provides ensemble voting logic including Union, Majority, Intersection,
    and configurable threshold agreement scores.
    """

    def _resolve_threshold(self, method: str, n_sois: int, user_threshold: float) -> float:
        """Determines the effective numerical threshold score based on the consensus method."""
        normalized_method = method.strip().lower()

        if normalized_method in ["union"]:
            return 1.0 / max(n_sois, 1)
        elif normalized_method in ["majority"]:
            return 0.5
        elif normalized_method in ["intersection"]:
            return 1.0
        else:
            # Custom consensus threshold
            return float(user_threshold)

    def _build_support_table(
        self, soi_dict_map: Dict[str, Sequence[Any]]
    ) -> pd.DataFrame:
        """
        Calculates solution support counts and consensus scores across selected SOIs.

        Parameters
        ----------
        soi_dict_map : Dict[str, Sequence[Any]]
            Mapping of SOI names to their respective list of solution IDs.
        """
        support: Dict[Any, int] = {}
        support_names: Dict[Any, List[str]] = {}
        n_sois = len(soi_dict_map)

        for soi_name, ids in soi_dict_map.items():
            unique_ids = set(ids)
            for solution_id in unique_ids:
                support[solution_id] = support.get(solution_id, 0) + 1
                support_names.setdefault(solution_id, []).append(soi_name)

        rows = []
        for solution_id, support_count in support.items():
            consensus_score = support_count / max(n_sois, 1)
            rows.append(
                {
                    "target_id": solution_id,
                    "consensus_support_count": support_count,
                    "consensus_score": consensus_score,
                    "consensus_supporting_sois": ", ".join(
                        sorted(support_names.get(solution_id, []))
                    ),
                }
            )

        return pd.DataFrame(rows)

    def evaluate(
        self,
        df: pd.DataFrame,
        soi_dict_map: Dict[str, Sequence[Any]],
        method: str = "Consensus Threshold",
        threshold: float = 0.5,
        id_col: str = "id",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Filters and enriches the input DataFrame based on consensus across source SOIs.

        Parameters
        ----------
        df : pd.DataFrame
            Input global solution space DataFrame.
        soi_dict_map : Dict[str, Sequence[Any]]
            Dictionary mapping SOI names to their list of solution IDs.
        method : str, default="Consensus Threshold"
            Consensus logic: "Union", "Majority", "Intersection", or "Consensus Threshold".
        threshold : float, default=0.5
            Custom threshold (0.0 to 1.0) applied when method is "Consensus Threshold".
        id_col : str, default="id"
            Column name containing unique solution identifiers.

        Returns
        -------
        pd.DataFrame
            Enriched DataFrame containing solutions that meet the consensus threshold.
        """
        if df.empty or not soi_dict_map or len(soi_dict_map) < 2:
            logger.warning("[%s] At least 2 SOIs are required for consensus evaluation.", self.__class__.__name__)
            return pd.DataFrame()

        support_table = self._build_support_table(soi_dict_map)
        if support_table.empty:
            logger.warning("[%s] No IDs found in the provided SOIs.", self.__class__.__name__)
            return pd.DataFrame()

        effective_threshold = self._resolve_threshold(
            method=method, n_sois=len(soi_dict_map), user_threshold=threshold
        )

        filtered_support = support_table[
            support_table["consensus_score"] >= effective_threshold
        ].copy()

        if filtered_support.empty:
            logger.info("[%s] No solutions met the required threshold score of %.2f", self.__class__.__name__, effective_threshold)
            return pd.DataFrame()

        result = df.copy()

        join_key = id_col if id_col in result.columns else result.index.name or "index"
        if id_col not in result.columns:
            result = result.reset_index()

        result = result.merge(
            filtered_support, left_on=join_key, right_on="target_id", how="inner"
        )

        if "target_id" in result.columns and target_id != join_key:
            result.drop(columns=["target_id"], inplace=True)

        n_sois = len(soi_dict_map)
        result["consensus_method"] = method
        result["consensus_threshold"] = effective_threshold
        result["consensus_total_sois"] = n_sois

        result = result.sort_values(
            ["consensus_score", "consensus_support_count", join_key],
            ascending=[False, False, True],
        ).copy()

        result["consensus_rank"] = range(1, len(result) + 1)

        return result

    def run(
        self,
        df: pd.DataFrame,
        soi_dict_map: Dict[str, Sequence[Any]],
        method: str = "Consensus Threshold",
        threshold: float = 0.5,
        id_col: str = "id",
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        """
        Runs consensus evaluation and returns a mapping with the consensus group.

        Returns
        -------
        Dict[str, List[Any]]
            Mapping containing consensus label and list of qualifying solution IDs.
        """
        evaluated_df = self.evaluate(
            df=df,
            soi_dict_map=soi_dict_map,
            method=method,
            threshold=threshold,
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

        effective_threshold = self._resolve_threshold(
            method=method, n_sois=len(soi_dict_map), user_threshold=threshold
        )

        group_key = f"Consensus [{method}] (Threshold >= {effective_threshold:.2f}, N={len(solution_ids)})"
        return {group_key: solution_ids}