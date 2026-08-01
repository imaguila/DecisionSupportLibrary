import streamlit as st
import pandas as pd


def apply_framing(dataset):

    df = dataset["df"].copy()

    dimensions = (
        dataset["metrics"]
        +
        dataset["selected_indicators"]
    )

    st.sidebar.markdown(
        "## Context Framing"
    )

    filtered_df = df.copy()

    for metric in dimensions:

        if metric not in filtered_df.columns:
            continue

        if not pd.api.types.is_numeric_dtype(
            filtered_df[metric]
        ):
            continue

        min_v = float(
            filtered_df[metric].min()
        )

        max_v = float(
            filtered_df[metric].max()
        )

        if min_v == max_v:
            continue


        st.sidebar.markdown(
            f"**{metric}**"
        )

        selected_range = st.sidebar.slider(
            metric,
            min_v,
            max_v,
            (min_v, max_v),
            key=f"slider_{metric}",
            label_visibility="collapsed"
        )

        col_min, col_max = st.sidebar.columns(2)

        with col_min:

            user_min = st.number_input(
                "Min",
                min_value=min_v,
                max_value=max_v,
                value=float(selected_range[0]),
                key=f"min_{metric}"
            )

        with col_max:

            user_max = st.number_input(
                "Max",
                min_value=min_v,
                max_value=max_v,
                value=float(selected_range[1]),
                key=f"max_{metric}"
            )

        filtered_df = filtered_df[

            (filtered_df[metric] >= user_min)

            &

            (filtered_df[metric] <= user_max)

        ]

    st.sidebar.metric(
        "Remaining Solutions",
        len(filtered_df)
    )

    return filtered_df