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

        selected_range = st.sidebar.slider(
            metric,
            min_v,
            max_v,
            (min_v, max_v)
        )

        filtered_df = filtered_df[

            (
                filtered_df[metric]
                >= selected_range[0]
            )

            &

            (
                filtered_df[metric]
                <= selected_range[1]
            )
        ]

    st.sidebar.metric(
        "Remaining Solutions",
        len(filtered_df)
    )

    return filtered_df