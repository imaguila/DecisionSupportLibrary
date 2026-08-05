"""
Visualization UI Module.

Provides interactive Plotly visualization components including scatter plots, 
coordinated dual-view maps, and statistical distribution charts (violin/box plots).
"""

from typing import List, Optional

import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================================
# COLOR SELECTION HELPERS
# =====================================================


def infer_lens_color_column(
    df: pd.DataFrame, user_color: Optional[str] = None
) -> Optional[str]:
    """
    Infers the optimal column to use for plot color encoding based on active lenses.

    Priority Order
    --------------
    1. group_label (Clustering / Indicator Dominance)
    2. cluster_str (Cluster ID string)
    3. preference_score (Preference Lens)
    4. efficiency_score (Efficiency Lens)
    5. consensus_score (Consensus Lens)
    6. domain_match_count (Domain Lens)
    7. user_color (User Fallback Selection)

    Parameters
    ----------
    df : pd.DataFrame
        Working solution space DataFrame.
    user_color : Optional[str]
        User-selected fallback color column name.

    Returns
    -------
    Optional[str]
        Inferred column name to be used for color encoding.
    """
    if df is None or df.empty:
        return user_color

    priority_cols = [
        "group_label",
        "cluster_str",
        "preference_score",
        "efficiency_score",
        "consensus_score",
        "domain_match_count",
    ]

    for col in priority_cols:
        if col in df.columns:
            return col

    return user_color


def is_discrete_color(df: pd.DataFrame, color_column: Optional[str]) -> bool:
    """
    Determines if a target color column should be rendered as discrete/categorical.

    Parameters
    ----------
    df : pd.DataFrame
        Working solution space DataFrame.
    color_column : Optional[str]
        Column name evaluated for discrete rendering.

    Returns
    -------
    bool
        True if the column should be treated as discrete; False otherwise.
    """
    if df is None or color_column is None or color_column not in df.columns:
        return False

    known_discrete = {
        "group_label",
        "cluster_str",
        "preference_method",
        "efficiency_method",
        "domain_matched_metrics",
    }

    if color_column in known_discrete:
        return True

    return pd.api.types.is_object_dtype(
        df[color_column]
    ) or pd.api.types.is_categorical_dtype(df[color_column])


def build_hover_columns(df: pd.DataFrame) -> List[str]:
    """
    Builds a clean list of non-internal columns to display in hover tooltips.

    Parameters
    ----------
    df : pd.DataFrame
        Working solution space DataFrame.

    Returns
    -------
    List[str]
        Filtered list of valid column names for hover tooltips.
    """
    if df is None or df.empty:
        return []

    excluded_prefixes = ("req_", "var_", "x_")
    excluded_cols = {"label", "highlight", "highlight_label"}

    return [
        col
        for col in df.columns
        if col not in excluded_cols and not col.startswith(excluded_prefixes)
    ]


# =====================================================
# SCATTER PLOT
# =====================================================


def render_scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    size: Optional[str] = None,
    color: Optional[str] = None,
    show_ids: bool = False,
    key: Optional[str] = None,
) -> None:
    """
    Renders an interactive Plotly scatter plot for two decision space dimensions.

    Parameters
    ----------
    df : pd.DataFrame
        Working solution space DataFrame.
    x : str
        Column name for x-axis.
    y : str
        Column name for y-axis.
    size : Optional[str], default=None
        Column name for bubble size encoding.
    color : Optional[str], default=None
        Column name or fallback for color encoding.
    show_ids : bool, default=False
        Whether to render solution ID text labels above data points.
    key : Optional[str], default=None
        Unique Streamlit widget identifier key.
    """
    if df is None or df.empty:
        st.warning("No data available for visualization.")
        return

    if x not in df.columns or y not in df.columns:
        st.warning("Selected axes are not available in the current dataset.")
        return

    plot_df = df.copy()
    text_column: Optional[str] = None

    if show_ids:
        if "id" in plot_df.columns:
            text_column = "id"
        elif "ID" in plot_df.columns:
            text_column = "ID"

    plot_color = infer_lens_color_column(plot_df, user_color=color)
    discrete_color = is_discrete_color(plot_df, plot_color)
    hover_cols = build_hover_columns(plot_df)

    if discrete_color and plot_color is not None:
        plot_df[plot_color] = plot_df[plot_color].astype(str)
        fig = px.scatter(
            plot_df,
            x=x,
            y=y,
            size=size,
            color=plot_color,
            text=text_column,
            hover_data=hover_cols,
        )
    else:
        fig = px.scatter(
            plot_df,
            x=x,
            y=y,
            size=size,
            color=plot_color,
            color_continuous_scale=px.colors.sequential.Viridis,
            text=text_column,
            hover_data=hover_cols,
        )

    fig.update_traces(
        textposition="top center",
        textfont=dict(size=10),
    )

    if "highlight" in plot_df.columns and plot_df["highlight"].any():
        marker_opacity = plot_df["highlight"].apply(
            lambda val: 1.0 if val else 0.25
        )
        fig.update_traces(marker=dict(opacity=marker_opacity))

    fig.update_layout(
        height=500,
        template="plotly_white",
        legend_title_text=plot_color if plot_color is not None else "",
    )

    st.plotly_chart(fig, use_container_width=True, key=key)


# =====================================================
# COORDINATED MAPS
# =====================================================


def render_coordinated_maps(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    key_prefix: str,
    show_ids: bool = False,
) -> None:
    """
    Renders two side-by-side scatter plots sharing a common x-axis dimension.

    Parameters
    ----------
    df : pd.DataFrame
        Working solution space DataFrame.
    x : str
        Common x-axis column name.
    y : str
        Left scatter plot y-axis column name.
    z : str
        Right scatter plot y-axis column name.
    key_prefix : str
        Prefix used to generate unique Streamlit widget keys.
    show_ids : bool, default=False
        Whether to display solution ID text labels on scatter plots.
    """
    col1, col2 = st.columns(2)

    with col1:
        st.caption(f"{x} vs {y}")
        render_scatter(
            df,
            x=x,
            y=y,
            show_ids=show_ids,
            key=f"{key_prefix}_left",
        )

    with col2:
        st.caption(f"{x} vs {z}")
        render_scatter(
            df,
            x=x,
            y=z,
            show_ids=show_ids,
            key=f"{key_prefix}_right",
        )


# =====================================================
# DISTRIBUTION VISUALIZATION
# =====================================================


def render_distribution(
    df: pd.DataFrame,
    metric: str,
    mode: str = "Violin",
    key: Optional[str] = None,
) -> None:
    """
    Renders a statistical distribution plot (Violin or Box plot) for a target metric.

    Parameters
    ----------
    df : pd.DataFrame
        Working solution space DataFrame.
    metric : str
        Target metric column name.
    mode : str, default="Violin"
        Plotting style, either "Violin" or "Box".
    key : Optional[str], default=None
        Unique Streamlit widget identifier key.
    """
    if df is None or df.empty:
        st.warning("No data available for visualization.")
        return

    if metric not in df.columns:
        st.warning("Selected metric is not available in the current dataset.")
        return

    if mode == "Violin":
        fig = px.violin(df, y=metric, box=True, points="all")
    else:
        fig = px.box(df, y=metric, points="all")

    fig.update_layout(
        title=f"Distribution of {metric}",
        height=550,
        showlegend=False,
        template="plotly_white",
    )

    st.plotly_chart(fig, use_container_width=True, key=key)