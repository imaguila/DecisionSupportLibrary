# metrics_catalog.py
import pandas as pd
from config import CASES
from column_rules import is_excluded_column


def get_metric_sets(df, case_name=None):
    """
    Categorizes DataFrame columns into base optimization metrics and 
    derived quality indicators based on the active case configuration or 
    dynamic dataset inference.

    Returns:
        - available_opt: base optimization objectives (e.g. satisfaction, effort, drag, weight)
        - available_qual: derived quality/domain indicators (e.g. productivity, lift_to_drag_ratio)
        - available_metrics: union of optimization and quality metrics
    """
    # 1. Identify base optimization metrics from active case config (if available)
    base_opt_metrics = []
    if case_name and case_name in CASES:
        base_opt_metrics = CASES[case_name].get("metrics", [])

    # 2. Select valid numeric columns (ignoring IDs, timestamps, and decision variables)
    analysis_cols = [
        col for col in df.columns
        if pd.api.types.is_numeric_dtype(df[col]) and not is_excluded_column(col)
    ]

    # 3. Separate into base optimization objectives vs quality/domain indicators
    if base_opt_metrics:
        available_opt = [c for c in analysis_cols if c in base_opt_metrics]
        available_qual = [c for c in analysis_cols if c not in base_opt_metrics]
    else:
        # Fallback for custom uploaded files: treat all numeric cols as analysis metrics
        available_opt = analysis_cols
        available_qual = []

    available_metrics = available_opt + available_qual

    return available_opt, available_qual, available_metrics
