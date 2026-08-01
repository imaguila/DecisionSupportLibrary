import plotly.express as px
import streamlit as st


def render_scatter(
    df,
    x,
    y,
    size=None,
    color=None
):

    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=color
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )