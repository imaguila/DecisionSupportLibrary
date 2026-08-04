## --------------------------------------------------------------------------------------
## css/css_comparison.py
## --------------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =====================================================
# BASIC HELPERS
# =====================================================

def get_numeric_dimensions(
    df,
    dataset
):

    dimensions = (
        dataset["metrics"]
        +
        dataset["selected_indicators"]
    )

    return [
        col
        for col in dimensions
        if (
            col in df.columns
            and pd.api.types.is_numeric_dtype(
                df[col]
            )
        )
    ]


def get_decision_variable_columns(
    df,
    dataset
):

    var_prefix = (
        dataset["config"]
        .get(
            "var_prefix",
            "x_"
        )
    )

    return [
        col
        for col in df.columns
        if col.startswith(
            var_prefix
        )
    ]


def normalize_metric(
    series,
    goal
):

    min_v = series.min()
    max_v = series.max()

    if max_v <= min_v:

        return pd.Series(
            0.5,
            index=series.index
        )

    normalized = (
        series
        -
        min_v
    ) / (
        max_v
        -
        min_v
    )

    if goal == "Minimize":

        normalized = (
            1.0
            -
            normalized
        )

    return normalized

# =====================================================
# TRADE-OFF RADAR
# =====================================================
# =====================================================
# TRADE-OFF RADAR
# =====================================================

def render_tradeoff_radar(
    compare_df,
    css_df,
    dataset
):

    numeric_dimensions = get_numeric_dimensions(
        css_df,
        dataset
    )

    if len(numeric_dimensions) < 3:

        st.info(
            "At least three numeric objectives or indicators are required "
            "to create a radar chart."
        )

        return

    selected_metrics = st.multiselect(
        "Objectives and indicators for radar profile",
        numeric_dimensions,
        default=numeric_dimensions[
            :min(
                5,
                len(numeric_dimensions)
            )
        ],
        key="css_tradeoff_metrics"
    )

    if len(selected_metrics) < 3:

        st.warning(
            "Select at least three objectives or indicators."
        )

        return

    metric_goals = {}

    cols = st.columns(
        len(selected_metrics)
    )

    for idx, metric in enumerate(
        selected_metrics
    ):
        
        metric_goals = {}

        cols = st.columns(
            len(selected_metrics)
        )

    for idx, metric in enumerate(
        selected_metrics
    ):

        col = cols[idx]

        with col:

            metric_goals[
                metric
            ] = st.selectbox(
                metric,
                [
                    "Maximize",
                    "Minimize"
                ],
                key=f"css_goal_{metric}"
            )


    radar_df = compare_df.copy()

    for metric in selected_metrics:

        radar_df[
            metric
        ] = normalize_metric(
            radar_df[metric],
            metric_goals[metric]
        )

    fig = go.Figure()

    for _, row in radar_df.iterrows():

        values = row[
            selected_metrics
        ].tolist()

        values.append(
            values[0]
        )

        theta = (
            selected_metrics
            +
            [
                selected_metrics[0]
            ]
        )

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=theta,
                mode="lines+markers",
                name=f"ID {int(row['id'])}"
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[
                    0,
                    1
                ]
            )
        ),
        showlegend=True,
        template="plotly_white",
        height=520
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# DECISION-VARIABLE MATRIX
# =====================================================

def render_decision_variable_matrix(
    compare_df,
    dataset
):

    variable_cols = get_decision_variable_columns(
        compare_df,
        dataset
    )

    var_prefix = (
        dataset["config"]
        .get(
            "var_prefix",
            "x_"
        )
    )

    if not variable_cols:

        st.info(
            f"No decision-variable columns with prefix "
            f"'{var_prefix}' found in the current CSS."
        )

        return

    matrix_df = (
        compare_df
        .set_index(
            "id"
        )[variable_cols]
        .copy()
    )

    matrix_df.index = [
        f"ID {int(idx)}"
        for idx in matrix_df.index
    ]

    fig = px.imshow(
        matrix_df,
        labels=dict(
            x="Decision variables",
            y="Solutions",
            color="Value"
        ),
        color_continuous_scale=[
            [
                0,
                "#e0e0e0"
            ],
            [
                1,
                "#00e676"
            ]
        ]
    )

    fig.update_layout(
        template="plotly_white",
        coloraxis_showscale=False,
        xaxis=dict(
            tickangle=-45,
            showgrid=False
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False
        ),
        height=520
    )

    fig.update_traces(
        xgap=3,
        ygap=3,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Variable: %{x}<br>"
            "Value: %{z}"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

