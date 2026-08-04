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

    # =====================================================
# DECISION-VARIABLE DISTRIBUTION
# =====================================================

def render_decision_variable_distribution(
    css_df,
    dataset
):

    variable_cols = get_decision_variable_columns(
        css_df,
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

    variable_summary = (
        css_df[variable_cols]
        .mean()
        .reset_index()
    )

    variable_summary.columns = [
        "decision_variable",
        "selection_rate"
    ]

    variable_summary = variable_summary.sort_values(
        "selection_rate",
        ascending=False
    )

    max_variables = min(
        50,
        len(variable_summary)
    )

    if max_variables < 1:

        st.info(
            "No decision variables can be summarized."
        )

        return

    top_n = st.slider(
        "Decision variables to show",
        min_value=1,
        max_value=max_variables,
        value=min(
            20,
            max_variables
        ),
        key="css_decision_variable_top_n"
    )

    plot_df = variable_summary.head(
        top_n
    )

    fig = px.bar(
        plot_df,
        x="decision_variable",
        y="selection_rate",
        labels={
            "decision_variable": "Decision variable",
            "selection_rate": "Selection rate in CSS"
        }
    )

    fig.update_layout(
        template="plotly_white",
        height=420,
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
# MAIN CSS COMPARISON
# =====================================================

def render_css_comparison(
    css_df,
    dataset
):

    if not st.session_state.get(
        "show_css_comparison",
        False
    ):

        return

    st.markdown(
        "## 🆚 Detailed comparison"
    )

    if css_df is None or css_df.empty:

        st.info(
            "No Candidate Solution Set is available for comparison."
        )

        return

    if "id" not in css_df.columns:

        st.warning(
            "The current CSS does not contain an 'id' column."
        )

        return

    css_ids = (
        css_df["id"]
        .dropna()
        .astype(int)
        .tolist()
    )

    default_ids = st.session_state.get(
        "css_highlight_ids",
        []
    )

    default_ids = [
        solution_id
        for solution_id in default_ids
        if solution_id in css_ids
    ]

    compare_ids = st.multiselect(
        "Pick solutions to compare",
        css_ids,
        default=default_ids,
        key="css_compare_ids"
    )

    if len(compare_ids) < 2:

        st.info(
            "Select at least 2 solutions to compare."
        )

        return

    compare_df = css_df[
        css_df["id"].isin(
            compare_ids
        )
    ].copy()

    tab1, tab2, tab3 = st.tabs(
        [
            "📊 Objectives and indicators",
            "📋 Decision-variable matrix",
            "📈 Decision-variable distribution"
        ]
    )

    with tab1:

        render_tradeoff_radar(
            compare_df,
            css_df,
            dataset
        )

    with tab2:

        render_decision_variable_matrix(
            compare_df,
            dataset
        )

    with tab3:

        render_decision_variable_distribution(
            css_df,
            dataset
        )
        