import streamlit as st

from core.visualization import (
    render_scatter
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
    # WORKSPACE STATE
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

    if "maps" not in st.session_state:

        st.session_state.maps = [

            {
                "x": dimensions[0],
                "y": dimensions[1],
                "size": None,
                "color": None,
            }

        ]

    # ==================================================
    # VISUAL WORKSPACE
    # ==================================================

    st.sidebar.markdown(
        "## Visual Workspace"
    )

    c1, c2 = st.sidebar.columns(2)

    with c1:

        if st.button(
            "Add Map",
            use_container_width=True
        ):

            st.session_state.maps.append(

                {
                    "x": dimensions[0],
                    "y": dimensions[1],
                    "size": None,
                    "color": None,
                }

            )

            st.rerun()

    with c2:

        if st.button(
            "Reset",
            use_container_width=True
        ):

            st.session_state.maps = [

                {
                    "x": dimensions[0],
                    "y": dimensions[1],
                    "size": None,
                    "color": None,
                }

            ]

            st.rerun()

    # ==================================================
    # RENDER MAPS
    # ==================================================

    for idx, current_map in enumerate(
        st.session_state.maps
    ):

        st.subheader(
            f"Decision-Space Map {idx+1}"
        )

        col_x, col_y, col_s, col_c = (
            st.columns(4)
        )

        with col_x:

            x = st.selectbox(
                "X Axis",
                dimensions,
                index=max(
                    0,
                    dimensions.index(
                        current_map["x"]
                    )
                ),
                key=f"x_{idx}"
            )

        with col_y:

            y_options = [
                d
                for d in dimensions
                if d != x
            ]

            current_y = (
                current_map["y"]
                if current_map["y"]
                in y_options
                else y_options[0]
            )

            y = st.selectbox(
                "Y Axis",
                y_options,
                index=y_options.index(
                    current_y
                ),
                key=f"y_{idx}"
            )

        with col_s:

            size = st.selectbox(
                "Bubble Size",
                [None] + dimensions,
                key=f"size_{idx}"
            )

        with col_c:

            color = st.selectbox(
                "Color",
                [None] + dimensions,
                key=f"color_{idx}"
            )

        # --------------------------------------
        # save state
        # --------------------------------------

        st.session_state.maps[idx] = {

            "x": x,
            "y": y,
            "size": size,
            "color": color,
        }

        render_scatter(
            df,
            x=x,
            y=y,
            size=size,
            color=color
        )

    # ==================================================
    # DATA TABLE
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