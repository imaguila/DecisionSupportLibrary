import streamlit as st

from core.visualization import (
    render_scatter
)


def render_workspace(
    df,
    dataset
):

    st.subheader(
        "Dataset Summary"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Solutions",
            len(df)
        )

    with c2:

        st.metric(
            "Attributes",
            len(df.columns)
        )

    with c3:

        st.metric(
            "Decision Variables",
            len(
                dataset[
                    "decision_variables"
                ]
            )
        )

    st.caption(
        "Decision-variable prefix: "
        f"{dataset['config'].get('var_prefix')}"
    )

    dimensions = (

        dataset["metrics"]

        +

        dataset["selected_indicators"]
    )

    if len(dimensions) < 2:

        st.warning(
            "At least two dimensions are required."
        )

        return

    st.subheader(
        "Decision Space Map"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        x = st.selectbox(
            "X axis",
            dimensions,
            index=0
        )

    with col2:

        y_options = [

            d

            for d in dimensions

            if d != x
        ]

        y = st.selectbox(
            "Y axis",
            y_options,
            index=0
        )

    with col3:

        size = st.selectbox(
            "Bubble size",
            [None] + dimensions,
            index=0
        )

    render_scatter(
        df,
        x,
        y,
        size=size
    )

    st.subheader(
        "Current Dataset"
    )

    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )