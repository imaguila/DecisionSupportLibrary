import plotly.express as px
import streamlit as st


def render_scatter(
    df,
    x,
    y,
    size=None,
    color=None,
    key=None
):

    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=color,
        hover_data=list(df.columns)
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
    key_prefix
):

    col1, col2 = st.columns(2)

    with col1:

        render_scatter(
            df,
            x=x,
            y=y,
            key=f"{key_prefix}_left"
        )

    with col2:

        render_scatter(
            df,
            x=x,
            y=z,
            key=f"{key_prefix}_right"
        )