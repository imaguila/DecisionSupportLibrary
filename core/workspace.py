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
    # VISUAL WORKSPACE
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

    st.sidebar.markdown(
        "## Visual Workspace"
    )

    col_reset, col_add = st.sidebar.columns(
        [0.35, 0.65]
    )

    with col_reset:

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

    with col_add:

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

    # ==================================================
    # MAPS
    # ==================================================

    for idx, current_map in enumerate(
        st.session_state.maps
    ):

        st.subheader(
            f"Decision-Space Map {idx+1}"
        )

        # ------------------------------------------
        # Axis configuration ABOVE the charts
        # ------------------------------------------

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            current_x = (
                current_map["x"]
                if current_map["x"] in dimensions
                else dimensions[0]
            )

            x = st.selectbox(
                "X Axis",
                dimensions,
                index=dimensions.index(
                    current_x
                ),
                key=f"x_{idx}"
            )

        with c2:

            current_y = (
                current_map["y"]
                if current_map["y"] in dimensions
                else dimensions[0]
            )

            y = st.selectbox(
                "Y Axis",
                dimensions,
                index=dimensions.index(
                    current_y
                ),
                key=f"y_{idx}"
            )

        with c3:

            current_z = (
                current_map["z"]
                if current_map["z"] in dimensions
                else dimensions[0]
            )

            z = st.selectbox(
                "Third Dimension",
                dimensions,
                index=dimensions.index(
                    current_z
                ),
                key=f"z_{idx}"
            )

        with c4:

            color_options = (
                [None]
                + dimensions
            )
