import streamlit as st

from core.visualization import (
    render_scatter,
    render_coordinated_maps
)


def render_workspace(
    df,
    dataset
):

    # ==================================================
    # SUMMARY
    # ==================================================

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
                dataset["decision_variables"]
            )
        )

    st.caption(
        f"Decision-variable prefix: "
        f"`{dataset['config'].get('var_prefix')}`"
    )

    # ==================================================
    # DIMENSIONS
    # ==================================================

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

    # ==================================================
    # SESSION STATE
    # ==================================================

    if "maps" not in st.session_state:

        z_default = (
            dimensions[2]
            if len(dimensions) > 2
            else dimensions[1]
        )

        st.session_state.maps = [

            {
                "x": dimensions[0],
                "y": dimensions[1],
                "z": z_default,
                "color": None
            }

        ]

    # ==================================================
    # VISUAL WORKSPACE
    # ==================================================

    st.sidebar.markdown(
        "## Visual Workspace"
    )

    cA, cB = st.sidebar.columns(2)

    with cA:

        if st.button(
            "Add Map",
            use_container_width=True
        ):

            z_default = (
                dimensions[2]
                if len(dimensions) > 2
                else dimensions[1]
            )

            st.session_state.maps.append(

                {
                    "x": dimensions[0],
                    "y": dimensions[1],
                    "z": z_default,
                    "color": None
                }

            )

            st.rerun()

    with cB:

        if st.button(
            "Reset",
            use_container_width=True
        ):

            z_default = (
                dimensions[2]
                if len(dimensions) > 2
                else dimensions[1]
            )

            st.session_state.maps = [

                {
                    "x": dimensions[0],
                    "y": dimensions[1],
                    "z": z_default,
                    "color": None
                }

            ]

            st.rerun()

    # ==================================================
    # MAPS
    # ==================================================

    for idx, current_map in enumerate(
        st.session_state.maps
    ):

        st.subheader(
            f"Decision-Space Map {idx+1}"
        )

        mode_tab1, mode_tab2 = st.tabs([
            "📊 Coordinated Maps",
            "🫧 Bubble Map"
        ])

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            x = st.selectbox(
                "X Axis",
                dimensions,
                key=f"x_{idx}"
            )

        with c2:

            y = st.selectbox(
                "Y Axis",
                dimensions,
                key=f"y_{idx}"
            )

        with c3:

            z = st.selectbox(
                "Third Dimension",
                dimensions,
                key=f"z_{idx}"
            )

        with c4:

            color = st.selectbox(
                "Color",
                [None] + dimensions,
                key=f"color_{idx}"
            )

        # =====================================
        # COORDINATED MAPS
        # =====================================

        with mode_tab1:

            render_coordinated_maps(
                df,
                x,
                y,
                z,
                key_prefix=f"coord_{idx}"
            )

        # =====================================
        # BUBBLE MAP
        # =====================================

        with mode_tab2:

            render_scatter(
                df,
                x=x,
                y=y,
                size=z,
                color=color,
                key=f"bubble_{idx}"
            )

        st.session_state.maps[idx] = {

            "x": x,
            "y": y,
            "z": z,
            "color": color
        }

    # ==================================================
    # DATA PREVIEW
    # ==================================================

    with st.expander(
        "📋 Current Dataset",
        expanded=False
    ):

        st.dataframe(
            df,
            use_container_width=True,
            height=500
        )