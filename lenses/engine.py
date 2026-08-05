"""
Lens Engine Module.

Provides execution and orchestration services for dynamic analytical lenses
within the decision space exploration framework.
"""

import logging
from typing import Any, Dict, Optional
import pandas as pd

from . import get_lens

logger = logging.getLogger(__name__)


def apply_lens(
    df: Optional[pd.DataFrame],
    lens_name: str,
    params: Dict[str, Any],
    dataset: Optional[Dict[str, Any]] = None,
) -> Optional[pd.DataFrame]:
    """
    Applies a selected analytical lens instance to a decision space DataFrame.

    Parameters
    ----------
    df : Optional[pd.DataFrame]
        Input dataset representing candidate solutions.
    lens_name : str
        Identifier of the lens to apply (e.g., 'topsis', 'kmeans', 'efficiency').
        Passing "None" or an empty string returns an unmodified copy of `df`.
    params : Dict[str, Any]
        User-defined parameters required by the specific lens implementation.
    dataset : Optional[Dict[str, Any]], optional
        Global dataset context metadata, if needed.

    Returns
    -------
    Optional[pd.DataFrame]
        Transformed/Enriched DataFrame after applying the lens, or input copy on fallback.
    """
    if df is None or df.empty:
        return df

    if not lens_name or lens_name.strip().lower() == "none":
        return df.copy()

    lens_instance = get_lens(lens_name)

    if lens_instance is None:
        logger.warning(
            "Lens '%s' not found in LENS_REGISTRY. Returning original DataFrame.",
            lens_name,
        )
        return df.copy()

    try:
        # Standardized evaluation pipeline via BaseLens interface
        return lens_instance.evaluate(df=df, **params)

    except Exception as e:
        logger.error("Error executing lens '%s': %s", lens_name, str(e), exc_info=True)
        # Safe fallback: prevents pipeline crashes
        return df.copy()