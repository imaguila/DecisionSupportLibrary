import streamlit as st

def render_soi_registry():
    if "saved_sois" not in st.session_state:
        st.session_state.saved_sois = []
    active_ids = None
    with st.expander(
        "📚 Saved SOIs",
        expanded=False
    ):
        if not st.session_state.saved_sois:
            st.info(
                "No saved SOIs."
            )
            return None

        for idx, soi in enumerate(
            st.session_state.saved_sois
        ):
            col1, col2, col3 = st.columns(
                [0.6, 0.2, 0.2]
            )
            with col1:
                st.caption(
                    f"{soi['name']} "
                    f"[{len(soi['ids'])}]"
                )
            with col2:
                if st.button(
                    "Load",
                    key=f"load_soi_{idx}"
                ):
                    active_ids = soi["ids"]
                    st.session_state[
                        "active_soi_ids"
                    ] = active_ids
                    st.session_state[
                        "active_soi_name"
                    ] = soi["name"]
                    st.session_state[
                        "active_lens"
                    ] = "None"
                    st.rerun()

            with col3:
                if st.button(
                    "🗑️",
                    key=f"delete_soi_{idx}"
                ):
                    st.session_state.saved_sois.pop(
                        idx
                    )
                    st.rerun()
        if (
            "active_soi_ids"
            in st.session_state
        ):
            st.success(
                f"Loaded SOI "
                f"({len(st.session_state.active_soi_ids)} solutions)"
            )

            if st.button(
                "Clear Loaded SOI",
                use_container_width=True
            ):
                del st.session_state[
                    "active_soi_ids"
                ]
                st.rerun()

        return st.session_state.get(
            "active_soi_ids"
        )