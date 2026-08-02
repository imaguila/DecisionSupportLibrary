import plotly.express as px
import streamlit as st

def render_scatter(
    df,
    x,
    y,
    size=None,
    color=None,
    show_ids=False,
    key=None
):

    text_column = None

    if show_ids:
        if "id" in df.columns:
            text_column = "id"
        elif "ID" in df.columns:
            text_column = "ID"

    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=color,
        text=text_column,
        hover_data=list(df.columns)
    )

    fig.update_traces(
        textposition="top center"
    )

    fig.update_layout(
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key
    )


def render_coordinated_maps(
    df,
    x,
    y,
    z,
    key_prefix,
    show_ids=False
):

    col1, col2 = st.columns(2)
    with col1:
        st.caption(
            f"{x} vs {y}"
        )

        render_scatter(
            df,
            x=x,
            y=y,
            show_ids=show_ids,
            key=f"{key_prefix}_left"
        )

    with col2:
        st.caption(
            f"{x} vs {z}"
        )

        render_scatter(
            df,
            x=x,
            y=z,
            show_ids=show_ids,
            key=f"{key_prefix}_right"
        )


def render_distribution(
    df,
    metric,
    mode="Violin",
    key=None
):

    if mode == "Violin":

        fig = px.violin(
            df,
            y=metric,
            box=True,
            points="all"
        )

    else:

        fig = px.box(
            df,
            y=metric,
            points="all"
        )

    fig.update_layout(
        title=f"Distribution of {metric}",
        height=550,
        showlegend=False,
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key
    )