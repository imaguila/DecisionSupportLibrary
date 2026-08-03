## --------------------------------------------------------------------------------------
## visualization.py

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

    # --------------------------------------------------
    # Automatic lens-aware color
    # --------------------------------------------------
    # Priority:
    # 1. Clustering / indicator groups
    # 2. Preference scores
    # 3. Efficiency scores
    # 4. User-selected color

    plot_color = color

    if "group_label" in df.columns:

        plot_color = "group_label"

    elif "cluster_str" in df.columns:

        plot_color = "cluster_str"

    elif "preference_score" in df.columns:

        plot_color = "preference_score"

    elif "efficiency_score" in df.columns:

        plot_color = "efficiency_score"

    elif "domain_match_count" in df.columns:

        plot_color = "domain_match_count"

    # --------------------------------------------------
    # Clean hover data
    # --------------------------------------------------

    hover_cols = [

        c

        for c in df.columns

        if not (
            c.startswith("req_")
            or c.startswith("var_")
            or c.startswith("x_")
        )

    ]

    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=plot_color,
        text=text_column,
        hover_data=hover_cols
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


def render_coordinated_maps( df, x, y, z, key_prefix, show_ids=False) :
    col1, col2 = st.columns(2)
    with col1:
        st.caption( f"{x} vs {y}" )
        render_scatter( df, x=x, y=y, show_ids=show_ids, key=f"{key_prefix}_left" )
    with col2:
        st.caption( f"{x} vs {z}" )
        render_scatter( df, x=x, y=z, show_ids=show_ids, key=f"{key_prefix}_right" )

def render_distribution( df, metric, mode="Violin", key=None ) :
    if mode == "Violin":
        fig = px.violin( df, y=metric, box=True, points="all" )
    else:
        fig = px.box( df, y=metric, points="all" )

    fig.update_layout( title=f"Distribution of {metric}",
        height=550, showlegend=False, template="plotly_white"
    )
    st.plotly_chart( fig, use_container_width=True, key=key )