"""
Lenses Package Initializer.

Exports the global lens registry mapping unique string keys to concrete lens classes.
"""

from typing import Any, Dict, List, Optional, Type

from .base import BaseLens
from .consensus import ConsensusLens
from .diversity import (
    AgglomerativeLens,
    HDBSCANLens,
    KMeansLens,
    KMedoidsLens,
)
from .efficiency import EfficiencyLens
from .indicator import IndicatorLens
from .manual import ManualSelectionLens
from .preference import (
    ReferencePointLens,
    TOPSISLens,
    VIKORLens,
    WeightedSumLens,
)

# =====================================================
# GLOBAL LENS REGISTRY
# =====================================================

LENS_REGISTRY: Dict[str, Type[BaseLens]] = {
    # Consensus Meta-Lens
    "consensus": ConsensusLens,
    # Indicator Lens
    "indicator": IndicatorLens,
    # Efficiency Lens
    "efficiency": EfficiencyLens,
    # Manual Selection Lens
    "manual": ManualSelectionLens,
    # Diversity Lenses
    "kmedoids": KMedoidsLens,
    "kmeans": KMeansLens,
    "agglomerative": AgglomerativeLens,
    "hdbscan": HDBSCANLens,
    # Preference / MCDM Lenses
    "weighted_sum": WeightedSumLens,
    "topsis": TOPSISLens,
    "vikor": VIKORLens,
    "reference_point": ReferencePointLens,
}

__all__ = [
    "BaseLens",
    "ConsensusLens",
    "IndicatorLens",
    "EfficiencyLens",
    "ManualSelectionLens",
    "KMedoidsLens",
    "KMeansLens",
    "AgglomerativeLens",
    "HDBSCANLens",
    "WeightedSumLens",
    "TOPSISLens",
    "VIKORLens",
    "ReferencePointLens",
    "LENS_REGISTRY",
    "get_lens",
    "list_lenses",
]


def list_lenses() -> List[str]:
    """Retrieves all registered analytical lens identifier keys."""
    return list(LENS_REGISTRY.keys())


def get_lens(lens_name: str) -> Optional[BaseLens]:
    """
    Instantiates and returns an analytical lens by key name.

    Parameters
    ----------
    lens_name : str
        Identifier key string (e.g., 'consensus', 'efficiency', 'kmeans', 'topsis').

    Returns
    -------
    Optional[BaseLens]
        An instance of the requested lens class, or None if unrecognized.
    """
    lens_cls = LENS_REGISTRY.get(lens_name.lower())
    if lens_cls is None:
        return None
    return lens_cls()