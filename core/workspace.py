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

    st.subheader("Dataset Summary")

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
    # AVAILABLE DIMENSIONS
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
                "color": None,
            }

        ]

    # ==================================================
    # VISUAL WORKSPACE
    # ==================================================

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
                    "color": None,
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
                    "color": None,
                }

            )

            st.rerun()

    # ==================================================
    # MAPS
    # ==================================================

    for idx in range(
        len(st.session_state.maps)
    ):

        current_map = (
            st.session_state.maps[idx]
        )

        st.subheader(
            f"Decision-Space Map {idx + 1}"
        )

        # --------------------------------------
        # Axis selectors ABOVE plots
        # --------------------------------------

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            x = st.selectbox(
                "X Axis",
                dimensions,
                index=dimensions.index(
                    current_map["x"]
                )
                if current_map["x"] in dimensions
                else 0,
                key=f"x_{idx}"
            )

        with c2:

            y = st.selectbox(
                "Y Axis",
                dimensions,
                index=dimensions.index(
                    current_map["y"]
                )
                if current_map["y"] in dimensions
                else 0,
                key=f"y_{idx}"
            )

        with c3:

            z = st.selectbox(
                "Third Dimension",
                dimensions,
                index=dimensions.index(
                    current_map["z"]
                )
                if current_map["z"] in dimensions
                else 0,
                key=f"z_{idx}"
            )

        with c4:

            color = st.selectbox(
                "Color",
                [None] + dimensions,
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

        with tab1:

            render_coordinated_maps(
                df,
                x=x,
                y=y,
                z=z,
                key_prefix=f"coord_{idx}"
            )

        with tab2:

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