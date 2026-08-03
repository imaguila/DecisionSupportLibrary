## --------------------------------------------------------------------------------------
## soi_registry.py

import streamlit as st


def render_soi_registry():

    if "saved_sois" not in st.session_state:

        st.session_state.saved_sois = []

    with st.expander(
        "📚 Saved SOIs",
        expanded=False
    ):

        if not st.session_state.saved_sois:

            st.info(
                "No saved SOIs."
            )

            return

        if (
            "active_soi_name"
            in st.session_state
        ):

            st.success(
                f"Active SOI: "
                f"{st.session_state.active_soi_name} "
                f"({len(st.session_state.active_soi_ids)} solutions)"
            )


            if st.button(
                "Clear Loaded SOI",
                use_container_width=True,
                key="clear_loaded_soi"
            ):

                if "active_soi_ids" in st.session_state:

                    del st.session_state[
                        "active_soi_ids"
                    ]

                if "active_soi_name" in st.session_state:

                    del st.session_state[
                        "active_soi_name"
                    ]

                st.rerun()

            st.markdown("---")

        for idx, soi in enumerate(
            st.session_state.saved_sois
        ):

            col1, col2, col3 = st.columns(
                [0.62, 0.19, 0.19]
            )

            with col1:

                st.caption(
                    f"{soi['name']} "
                    f"[{len(soi['ids'])}] · "
                    f"{soi.get('lens', 'Unknown')}"
                )

            with col2:

                if st.button(
                    "Load",
                    key=f"load_soi_{idx}",
                    use_container_width=True
                ):

                    st.session_state[
                        "active_soi_ids"
                    ] = soi["ids"]

                    st.session_state[
                        "active_soi_name"
                    ] = soi["name"]

                    st.session_state[
                        "pending_lens_reset"
                    ] = True

                    st.rerun()


            with col3:

                if st.button(
                    "🗑️",
                    key=f"delete_soi_{idx}",
                    use_container_width=True
                ):

                    deleted_name = (
                        st.session_state.saved_sois[idx]["name"]
                    )

                    st.session_state.saved_sois.pop(
                        idx
                    )

                    if (
                        st.session_state.get(
                            "active_soi_name"
                        )
                        == deleted_name
                    ):

                        if "active_soi_ids" in st.session_state:

                            del st.session_state[
                                "active_soi_ids"
                            ]

                        if "active_soi_name" in st.session_state:

                            del st.session_state[
                                "active_soi_name"
                            ]

                    st.rerun()