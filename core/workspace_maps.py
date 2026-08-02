import streamlit as st

from core.visualization import (
    render_scatter,
    render_coordinated_maps,
    render_distribution
)


def render_maps(
    df,
    dataset,
    dimensions,
    show_ids
):
    if len(st.session_state.maps) == 0:

        st.info(
            "No decision maps have been created yet. "
            "Use 'New Map' in the Visual Workspace panel."
        )

        return
    for idx in range(
        len(st.session_state.maps)
    ):
        current_map = (
            st.session_state.maps[idx]
        )

        with st.expander(
            f"🗺️ Decision-Space Map {idx + 1}",
            expanded=(idx == 0)
        ):

            if len(dimensions) < 2:

                st.warning(
                    "At least two dimensions are required."
                )

                continue

            # =====================================
            # VISUALIZATION MODE
            # =====================================

            map_mode = st.radio(
                "Visualization Mode",
                [
                    "🗺️ Scatter",
                    "🫧 Bubble",
                    "📈 Distribution"
                ],
                horizontal=True,
                key=f"map_mode_{idx}"
            )

            # =====================================
            # SCATTER / BUBBLE
            # =====================================

            if map_mode in [
                "🗺️ Scatter",
                "🫧 Bubble"
            ]:

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

                if map_mode == "🗺️ Scatter":

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

                else:

                    render_scatter(
                        df,
                        x=x,
                        y=y,
                        size=(
                            z
                            if z is not None
                            else None
                        ),
                        color=color,
                        show_ids=show_ids,
                        key=f"bubble_{idx}"
                    )

            # =====================================
            # DISTRIBUTION
            # =====================================

            else:

                x = current_map["x"]
                y = current_map["y"]
                z = None
                color = None

                view_type = st.radio(
                    "View",
                    [
                        "Violin",
                        "Box"
                    ],
                    horizontal=True,
                    key=f"dist_mode_{idx}"
                )

                distribution_metric = st.selectbox(
                    "Dimension",
                    dimensions,
                    key=f"distribution_{idx}"
                )

                render_distribution(
                    df,
                    metric=distribution_metric,
                    mode=view_type,
                    key=f"distribution_plot_{idx}"
                )

            # =====================================
            # SAVE MAP STATE
            # =====================================

            st.session_state.maps[idx] = {

                "x": x,
                "y": y,
                "z": z,
                "color": color

            }