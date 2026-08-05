"""
Preference Lenses Module.

Implements standalone Multi-Criteria Decision Making (MCDM) analytical lenses
inheriting from a shared base preference engine.
"""

import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from .base import BaseLens

logger = logging.getLogger(__name__)

EPS: float = 1e-9


class BasePreferenceLens(BaseLens):
    """
    Abstract Base Class for all Preference/MCDM Lenses.
    
    Provides shared normalization, weighting, and boundary validation utilities.
    """

    def _prepare_inputs(
        self,
        df: pd.DataFrame,
        feature_cols: Sequence[str],
        weights: Optional[Dict[str, float]] = None,
        is_minimized: Optional[Dict[str, bool]] = None,
    ) -> Optional[Tuple[pd.DataFrame, List[str], np.ndarray, np.ndarray]]:
        """Validates features, handles missing data, and builds normalized weights & direction vectors."""
        if df.empty or not feature_cols:
            return None

        valid_cols = [c for c in feature_cols if c in df.columns]
        if not valid_cols:
            logger.warning("[%s] No valid feature columns found.", self.__class__.__name__)
            return None

        clean_df = df.dropna(subset=valid_cols).copy()
        if clean_df.empty:
            return None

        # Normalize weights vector
        if weights is None:
            w = np.ones(len(valid_cols)) / len(valid_cols)
        else:
            raw_w = np.array([weights.get(c, 1.0) for c in valid_cols], dtype=float)
            w_sum = np.sum(raw_w)
            w = raw_w / (w_sum if w_sum > 0 else 1.0)

        # Optimization directions mask (True = Minimize, False = Maximize)
        if is_minimized is None:
            min_mask = np.zeros(len(valid_cols), dtype=bool)
        else:
            min_mask = np.array([is_minimized.get(c, False) for c in valid_cols], dtype=bool)

        return clean_df, valid_cols, w, min_mask

    def _minmax_norm(
        self, df: pd.DataFrame, cols: List[str], min_mask: np.ndarray
    ) -> np.ndarray:
        """Applies oriented Min-Max normalization (1.0 is always optimal)."""
        vals = df[cols].to_numpy(dtype=float)
        min_v = np.min(vals, axis=0)
        max_v = np.max(vals, axis=0)
        ranges = max_v - min_v
        ranges[ranges == 0] = EPS

        norm = (vals - min_v) / ranges
        norm[:, min_mask] = 1.0 - norm[:, min_mask]
        return norm


# =============================================================================
# CONCRETE MCDM LENS IMPLEMENTATIONS
# =============================================================================

class WeightedSumLens(BasePreferenceLens):
    """Weighted Sum Model (WSM) Preference Lens."""

    def run(
        self,
        df: pd.DataFrame,
        feature_cols: Sequence[str],
        id_col: str = "id",
        weights: Optional[Dict[str, float]] = None,
        is_minimized: Optional[Dict[str, bool]] = None,
        top_n: int = 10,
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        prepared = self._prepare_inputs(df, feature_cols, weights, is_minimized)
        if prepared is None:
            return {}

        clean_df, valid_cols, w, min_mask = prepared
        norm = self._minmax_norm(clean_df, valid_cols, min_mask)
        scores = np.sum(norm * w, axis=1)

        return self._format_output(clean_df, scores, id_col, top_n, "Weighted Sum")


class TOPSISLens(BasePreferenceLens):
    """TOPSIS Preference Lens."""

    def run(
        self,
        df: pd.DataFrame,
        feature_cols: Sequence[str],
        id_col: str = "id",
        weights: Optional[Dict[str, float]] = None,
        is_minimized: Optional[Dict[str, bool]] = None,
        top_n: int = 10,
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        prepared = self._prepare_inputs(df, feature_cols, weights, is_minimized)
        if prepared is None:
            return {}

        clean_df, valid_cols, w, min_mask = prepared
        vals = clean_df[valid_cols].to_numpy(dtype=float)

        norms = np.linalg.norm(vals, axis=0)
        norms[norms == 0] = EPS
        weighted_norm = (vals / norms) * w

        ideal_best = np.zeros(len(valid_cols))
        ideal_worst = np.zeros(len(valid_cols))

        for j in range(len(valid_cols)):
            if min_mask[j]:
                ideal_best[j] = np.min(weighted_norm[:, j])
                ideal_worst[j] = np.max(weighted_norm[:, j])
            else:
                ideal_best[j] = np.max(weighted_norm[:, j])
                ideal_worst[j] = np.min(weighted_norm[:, j])

        d_plus = np.linalg.norm(weighted_norm - ideal_best, axis=1)
        d_minus = np.linalg.norm(weighted_norm - ideal_worst, axis=1)

        denom = d_plus + d_minus
        denom[denom == 0] = EPS
        scores = d_minus / denom

        return self._format_output(clean_df, scores, id_col, top_n, "TOPSIS")


class VIKORLens(BasePreferenceLens):
    """VIKOR Compromise Ranking Preference Lens."""

    def run(
        self,
        df: pd.DataFrame,
        feature_cols: Sequence[str],
        id_col: str = "id",
        weights: Optional[Dict[str, float]] = None,
        is_minimized: Optional[Dict[str, bool]] = None,
        top_n: int = 10,
        v_vikor: float = 0.5,
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        prepared = self._prepare_inputs(df, feature_cols, weights, is_minimized)
        if prepared is None:
            return {}

        clean_df, valid_cols, w, min_mask = prepared
        vals = clean_df[valid_cols].to_numpy(dtype=float)
        n_cols = len(valid_cols)

        f_best = np.zeros(n_cols)
        f_worst = np.zeros(n_cols)

        for j in range(n_cols):
            if min_mask[j]:
                f_best[j] = np.min(vals[:, j])
                f_worst[j] = np.max(vals[:, j])
            else:
                f_best[j] = np.max(vals[:, j])
                f_worst[j] = np.min(vals[:, j])

        ranges = np.abs(f_best - f_worst)
        ranges[ranges == 0] = EPS

        regret = w * (np.abs(f_best - vals) / ranges)
        s_vec = np.sum(regret, axis=1)
        r_vec = np.max(regret, axis=1)

        s_range = np.max(s_vec) - np.min(s_vec)
        r_range = np.max(r_vec) - np.min(r_vec)

        s_norm = (s_vec - np.min(s_vec)) / (s_range if s_range > 0 else EPS)
        r_norm = (r_vec - np.min(r_vec)) / (r_range if r_range > 0 else EPS)

        q_vec = v_vikor * s_norm + (1.0 - v_vikor) * r_norm
        scores = 1.0 - q_vec  # Invert so higher is better

        return self._format_output(clean_df, scores, id_col, top_n, "VIKOR")


class ReferencePointLens(BasePreferenceLens):
    """Reference Point Distance Preference Lens."""

    def run(
        self,
        df: pd.DataFrame,
        feature_cols: Sequence[str],
        id_col: str = "id",
        weights: Optional[Dict[str, float]] = None,
        is_minimized: Optional[Dict[str, bool]] = None,
        top_n: int = 10,
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        prepared = self._prepare_inputs(df, feature_cols, weights, is_minimized)
        if prepared is None:
            return {}

        clean_df, valid_cols, w, min_mask = prepared
        norm = self._minmax_norm(clean_df, valid_cols, min_mask)
        
        distances = np.sqrt(np.sum(w * ((1.0 - norm) ** 2), axis=1))
        max_dist = np.max(distances)
        scores = 1.0 - (distances / (max_dist if max_dist > 0 else EPS))

        return self._format_output(clean_df, scores, id_col, top_n, "Reference Point")

    # =========================================================================
    # COMMON OUTPUT HELPER
    # =========================================================================

    def _format_output(
        self,
        df: pd.DataFrame,
        scores: np.ndarray,
        id_col: str,
        top_n: int,
        method_name: str,
    ) -> Dict[str, List[Any]]:
        """Utility method shared across MCDM implementations to format output dictionary."""
        df["_score"] = scores
        sorted_df = df.sort_values(by="_score", ascending=False)

        effective_top_n = max(1, min(int(top_n), len(sorted_df)))
        top_df = sorted_df.head(effective_top_n)

        solution_ids = top_df[id_col].tolist() if id_col in top_df.columns else top_df.index.tolist()
        group_label = f"Top {effective_top_n} ({method_name})"

        return {group_label: solution_ids}


# Ensure BasePreferenceLens also has access to _format_output
BasePreferenceLens._format_output = ReferencePointLens._format_output