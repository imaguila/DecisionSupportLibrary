import streamlit as st


def render_workspace_controls(
    dimensions
):

    with st.sidebar.expander(
        "🗺️ Visual Workspace",
        expanded=False
    ):

        col1, col2 = st.columns(
            [0.35, 0.65]
        )

        if "maps" not in st.session_state:
            st.session_state.maps = [
                {
                    "x": dimensions[0],
                    "y": dimensions[1],
                    "z": None,
                    "color": None
                }

            ]

        with col1:

            if st.button(
                "Reset Maps",
                use_container_width=True
            ):

                st.session_state.maps = [

                    {
                        "x": dimensions[0],
                        "y": dimensions[1],
                        "z": None,
                        "color": None
                    }

                ]

                st.rerun()

        with col2:

            if st.button(
                "New Decision Map",
                use_container_width=True
            ):

                st.session_state.maps.append(

                    {
                        "x": dimensions[0],
                        "y": dimensions[1],
                        "z": None,
                        "color": None
                    }

                )

                st.rerun()

        show_ids = st.checkbox(
            "Show solution IDs",
            value=False
        )

        st.caption(
            f"Active maps: "
            f"{len(st.session_state.maps)}"
        )

    return show_ids