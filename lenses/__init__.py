"""
Lenses Package Initialization (lenses/__init__.py)
"""

import logging
from typing import Dict, List, Optional, Type, Union

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

logger = logging.getLogger(__name__)

# Registry mapping lens keys to either Lens classes or instantiated objects
LENS_REGISTRY: Dict[str, Union[Type[BaseLens], BaseLens]] = {
    "none": BaseLens,
    "indicator": IndicatorLens,
    "efficiency": EfficiencyLens,
    "manual": ManualSelectionLens,
    "kmeans": KMeansLens,
    "kmedoids": KMedoidsLens,
    "agglomerative": AgglomerativeLens,
    "hdbscan": HDBSCANLens,
    "weighted_sum": WeightedSumLens,
    "topsis": TOPSISLens,
    "vikor": VIKORLens,
    "reference_point": ReferencePointLens,
    "consensus": ConsensusLens,
}


def list_lenses() -> List[str]:
    """Returns list of registered lens keys excluding 'none'."""
    return [k for k in LENS_REGISTRY.keys() if k != "none"]


def get_lens(name: str) -> Optional[BaseLens]:
    """
    Safely retrieves a lens instance by name.
    """
    if not name:
        return None

    key = str(name).lower().strip()
    lens_item = LENS_REGISTRY.get(key)

    if lens_item is None:
        logger.warning("Lens '%s' not found in registry.", key)
        return None

    # Handle class types vs pre-instantiated objects safely
    if isinstance(lens_item, type):
        try:
            return lens_item()
        except Exception as e:
            logger.error("Failed to instantiate lens class '%s': %s", key, e)
            return None

    return lens_item