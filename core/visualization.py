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
    key_prefix
):

    col1, col2 = st.columns(2)

    with col1:

        st.caption(f"{x} vs {y}")

        render_scatter(
            df,
            x=x,
            y=y,
            key=f"{key_prefix}_left"
        )

    with col2:

        st.caption(f"{x} vs {z}")

        render_scatter(
            df,
            x=x,
            y=z,
            key=f"{key_prefix}_right"
        )