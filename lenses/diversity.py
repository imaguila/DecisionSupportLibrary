"""
Diversity Lenses Module.

Implements distance-based and density-based unsupervised learning algorithms 
(K-Medoids, K-Means, Agglomerative, HDBSCAN) as standalone analytical lenses.
"""

import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# Optional dependencies with safe fallback
try:
    from sklearn_extra.cluster import KMedoids
except (ImportError, ValueError, Exception) as e:
    import logging
    logging.warning("Could not load KMedoids from sklearn_extra: %s", e)
    KMedoids = None

try:
    from sklearn.cluster import HDBSCAN
except ImportError:
    HDBSCAN = None

from .base import BaseLens

logger = logging.getLogger(__name__)


class BaseDiversityLens(BaseLens):
    """
    Abstract base class for all diversity and clustering lenses.

    Provides common feature matrix standardization, silhouette score evaluation,
    and cluster output formatting utilities.
    """

    def _prepare_matrix(
        self, df: pd.DataFrame, feature_cols: Sequence[str]
    ) -> Optional[Tuple[pd.DataFrame, np.ndarray, List[str]]]:
        """Validates numeric feature presence, imputes NaNs, and standardizes via Z-score."""
        if df.empty or not feature_cols:
            return None

        valid_cols = [
            c
            for c in feature_cols
            if c in df.columns and pd.api.types.is_numeric_dtype(df[c])
        ]
        if not valid_cols:
            logger.warning("[%s] No valid numeric columns found.", self.__class__.__name__)
            return None

        clean_df = df.dropna(subset=valid_cols).copy()
        if len(clean_df) < 2:
            return None

        x = clean_df[valid_cols].copy()
        x = x.fillna(x.median(numeric_only=True)).fillna(0.0)

        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x)

        return clean_df, x_scaled, valid_cols

    def _compute_auto_k(
        self, x_scaled: np.ndarray, model_factory: Any, max_k: int = 10
    ) -> int:
        """Determines optimal cluster count k by maximizing silhouette score."""
        n_samples = len(x_scaled)
        if n_samples < 3:
            return 2

        best_k = 2
        best_score = -1.0
        upper_k = min(max_k, n_samples - 1)

        for k in range(2, upper_k + 1):
            try:
                model = model_factory(k)
                labels = model.fit_predict(x_scaled)
                unique_labels = set(labels)

                if 1 < len(unique_labels) < n_samples:
                    score = float(silhouette_score(x_scaled, labels))
                    if score > best_score:
                        best_score = score
                        best_k = k
            except Exception as exc:
                logger.debug("[%s] Silhouette score failed for k=%d: %s", self.__class__.__name__, k, exc)

        return best_k

    def _format_clusters(
        self,
        clean_df: pd.DataFrame,
        labels: np.ndarray,
        id_col: str = "id",
        exclude_noise: bool = False,
    ) -> Dict[str, List[Any]]:
        """Formats cluster labels into the standardized group output mapping."""
        if len(labels) == 0:
            return {}

        solution_ids = (
            clean_df[id_col].tolist()
            if id_col in clean_df.columns
            else clean_df.index.tolist()
        )

        groups: Dict[str, List[Any]] = {}
        unique_labels = sorted(list(set(labels)))

        for label in unique_labels:
            if label == -1 and exclude_noise:
                continue

            mask = labels == label
            member_ids = [solution_ids[i] for i, m in enumerate(mask) if m]

            if label == -1:
                group_name = f"Noise (N={len(member_ids)})"
            else:
                group_name = f"Cluster {label + 1} (N={len(member_ids)})"

            groups[group_name] = member_ids

        return groups


# =============================================================================
# CONCRETE DIVERSITY LENS IMPLEMENTATIONS
# =============================================================================


class KMedoidsLens(BaseDiversityLens):
    """K-Medoids partitioning diversity lens."""

    def run(
        self,
        df: pd.DataFrame,
        feature_cols: Sequence[str],
        id_col: str = "id",
        k: Optional[int] = None,
        auto_k: bool = False,
        max_k: int = 10,
        random_state: int = 123,
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        prepared = self._prepare_matrix(df, feature_cols)
        if prepared is None:
            return {}

        clean_df, x_scaled, _ = prepared

        def model_factory(n_clusters: int) -> Any:
            if KMedoids is not None:
                return KMedoids(n_clusters=n_clusters, method="pam", random_state=random_state)
            logger.warning("[KMedoidsLens] KMedoids unavailable, falling back to KMeans.")
            return KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)

        if auto_k or k is None:
            effective_k = self._compute_auto_k(x_scaled, model_factory, max_k=max_k)
        else:
            effective_k = max(2, min(int(k), len(clean_df)))

        model = model_factory(effective_k)
        labels = model.fit_predict(x_scaled)

        return self._format_clusters(clean_df, labels, id_col=id_col)


class KMeansLens(BaseDiversityLens):
    """K-Means partitioning diversity lens."""

    def run(
        self,
        df: pd.DataFrame,
        feature_cols: Sequence[str],
        id_col: str = "id",
        k: Optional[int] = None,
        auto_k: bool = False,
        max_k: int = 10,
        random_state: int = 123,
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        prepared = self._prepare_matrix(df, feature_cols)
        if prepared is None:
            return {}

        clean_df, x_scaled, _ = prepared

        def model_factory(n_clusters: int) -> KMeans:
            return KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)

        if auto_k or k is None:
            effective_k = self._compute_auto_k(x_scaled, model_factory, max_k=max_k)
        else:
            effective_k = max(2, min(int(k), len(clean_df)))

        model = model_factory(effective_k)
        labels = model.fit_predict(x_scaled)

        return self._format_clusters(clean_df, labels, id_col=id_col)


class AgglomerativeLens(BaseDiversityLens):
    """Agglomerative Hierarchical Clustering diversity lens."""

    def run(
        self,
        df: pd.DataFrame,
        feature_cols: Sequence[str],
        id_col: str = "id",
        k: Optional[int] = None,
        auto_k: bool = False,
        max_k: int = 10,
        distance_threshold: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        prepared = self._prepare_matrix(df, feature_cols)
        if prepared is None:
            return {}

        clean_df, x_scaled, _ = prepared

        if distance_threshold is not None:
            model = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=distance_threshold,
                compute_full_tree=True,
            )
        else:
            def model_factory(n_clusters: int) -> AgglomerativeClustering:
                return AgglomerativeClustering(n_clusters=n_clusters)

            if auto_k or k is None:
                effective_k = self._compute_auto_k(x_scaled, model_factory, max_k=max_k)
            else:
                effective_k = max(2, min(int(k), len(clean_df)))

            model = model_factory(effective_k)

        labels = model.fit_predict(x_scaled)
        return self._format_clusters(clean_df, labels, id_col=id_col)


class HDBSCANLens(BaseDiversityLens):
    """Density-based HDBSCAN clustering diversity lens."""

    def run(
        self,
        df: pd.DataFrame,
        feature_cols: Sequence[str],
        id_col: str = "id",
        min_cluster_size: Optional[int] = None,
        granularity: str = "Medium (~10%)",
        exclude_noise: bool = True,
        **kwargs: Any,
    ) -> Dict[str, List[Any]]:
        if HDBSCAN is None:
            logger.warning("[HDBSCANLens] HDBSCAN module not installed.")
            return {}

        prepared = self._prepare_matrix(df, feature_cols)
        if prepared is None:
            return {}

        clean_df, x_scaled, _ = prepared
        n_samples = len(clean_df)

        if min_cluster_size is None:
            if granularity == "Small (~5%)":
                ratio = 0.05
            elif granularity == "Large (~20%)":
                ratio = 0.20
            else:
                ratio = 0.10
            effective_size = max(2, int(ratio * n_samples))
        else:
            effective_size = max(2, min(int(min_cluster_size), n_samples))

        model = HDBSCAN(min_cluster_size=effective_size)
        labels = model.fit_predict(x_scaled)

        return self._format_clusters(
            clean_df, labels, id_col=id_col, exclude_noise=exclude_noise
        )