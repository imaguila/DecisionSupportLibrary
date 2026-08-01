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

    with st.expander(
        "📊 Dataset Summary",
        expanded=False
    ):

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
            f"{dataset['config'].get('var_prefix')}"
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

        st.session_state.maps = [

            {
                "x": dimensions[0],
                "y": dimensions[1],
                "z": None,
                "color": None,
            }

        ]

    # ==================================================
    # VISUAL WORKSPACE
    # ==================================================

    with st.sidebar.expander(
        "🗺️ Visual Workspace",
        expanded=False
    ):

        col_reset, col_add = st.columns(
            [0.35, 0.65]
        )

        with col_reset:

            if st.button(
                "Reset Maps",
                use_container_width=True
            ):

                st.session_state.maps = [

                    {
                        "x": dimensions[0],
                        "y": dimensions[1],
                        "z": None,
                        "color": None,
                    }

                ]

                st.rerun()

        with col_add:

            if st.button(
                "New Decision Map",
                use_container_width=True
            ):

                st.session_state.maps.append(

                    {
                        "x": dimensions[0],
                        "y": dimensions[1],
                        "z": None,
                        "color": None,
                    }

                )

                st.rerun()

        st.caption(
            f"Active maps: {len(st.session_state.maps)}"
        )

        show_ids = st.checkbox(
            "Show IDs on plots",
            value=False
        )

    # ==================================================
    # MAPS
    # ==================================================

    for idx in range(
        len(st.session_state.maps)
    ):

        current_map = (
            st.session_state.maps[idx]
        )

        map_title = (
            f"🗺️ Decision-Space Map {idx + 1}"
        )

        with st.expander(
            map_title,
            expanded=(idx == 0)
        ):

            # --------------------------------------
            # Axis selectors
            # --------------------------------------

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

                y_options = [
                    d
                    for d in dimensions
                    if d != x
                ]

                current_y = (
                    current_map["y"]
                    if current_map["y"] in y_options
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

            with c3:

                z_options = [None] + [
                    d
                    for d in dimensions
                    if d not in [x, y]
                ]

                current_z = (
                    current_map["z"]
                    if current_map["z"] in z_options
                    else None
                )

                z = st.selectbox(
                    "Third Dimension",
                    z_options,
                    index=z_options.index(
                        current_z
                    ),
                    key=f"z_{idx}"
                )

            with c4:

                color_options = (
                    [None]
                    + dimensions
                )

                current_color = (
                    current_map["color"]
                    if current_map["color"]
                    in color_options
                    else None
                )

                color = st.selectbox(
                    "Color",
                    color_options,
                    index=color_options.index(
                        current_color
                    ),
                    key=f"color_{idx}"
                )

            # --------------------------------------
            # Tabs
            # --------------------------------------

            tab1, tab2 = st.tabs(
                [
                    "📊 Coordinated Maps",
                    "🫧 Bubble Map"
                ]
            )

            # =====================================
            # COORDINATED MAPS
            # =====================================

            with tab1:

                if z is None:

                    render_scatter(
                        df,
                        x=x,
                        y=y,
                        color=color,
                        show_ids=show_ids,
                        key=f"single_{idx}"
                    )

                else:

                    render_coordinated_maps(
                        df,
                        x=x,
                        y=y,
                        z=z,
                        key_prefix=f"coord_{idx}",
                        show_ids=show_ids
                    )

            # =====================================
            # BUBBLE MAP
            # =====================================

            with tab2:

                render_scatter(
                    df,
                    x=x,
                    y=y,
                    size=z if z is not None else None,
                    color=color,
                    show_ids=show_ids,
                    key=f"bubble_{idx}"
                )

            # --------------------------------------
            # Save map state
            # --------------------------------------

            st.session_state.maps[idx] = {

                "x": x,
                "y": y,
                "z": z,
                "color": color,
            }
    # ==================================================
    # EXPORT
    # ==================================================

    st.download_button(
        label="⬇️ Export Current Subset",
        data=df.to_csv(index=False),
        file_name="current_subset.csv",
        mime="text/csv"
    )

    # ==================================================
    # DATASET
    # ==================================================

    with st.expander(
        f"📋 Current Dataset (prefix: {dataset['config'].get('var_prefix')})",
        expanded=False
    ):

        st.dataframe(
            df,
            use_container_width=True,
            height=500
        )