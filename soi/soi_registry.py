## --------------------------------------------------------------------------------------
## soi/soi_registry.py
## --------------------------------------------------------------------------------------

import streamlit as st


# =====================================================
# SESSION STATE
# =====================================================

def ensure_soi_state():

    if "saved_sois" not in st.session_state:

        st.session_state.saved_sois = []


def has_loaded_soi():

    return (
        "active_soi_name"
        in st.session_state
        and
        "active_soi_ids"
        in st.session_state
    )


def clear_loaded_soi():

    if "active_soi_ids" in st.session_state:

        del st.session_state[
            "active_soi_ids"
        ]

    if "active_soi_name" in st.session_state:

        del st.session_state[
            "active_soi_name"
        ]

    st.session_state[
        "pending_lens_reset"
    ] = True


def load_soi(
    soi
):

    st.session_state[
        "active_soi_ids"
    ] = soi[
        "ids"
    ]

    st.session_state[
        "active_soi_name"
    ] = soi[
        "name"
    ]

    st.session_state[
        "pending_lens_reset"
    ] = True


def delete_soi(
    idx
):

    deleted_name = (
        st.session_state
        .saved_sois[idx]["name"]
    )

    st.session_state.saved_sois.pop(
        idx
    )

    if (
        st.session_state.get(
            "active_soi_name"
        )
        ==
        deleted_name
    ):

        clear_loaded_soi()


# =====================================================
# RENDER LOADED SOI
# =====================================================

def render_loaded_soi_status():

    if not has_loaded_soi():

        return

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

        clear_loaded_soi()

        st.rerun()

    st.markdown(
        "---"
    )


# =====================================================
# RENDER SAVED SOI ROW
# =====================================================

def render_saved_soi_row(
    soi,
    idx
):

    col1, col2, col3 = st.columns(
        [
            0.62,
            0.19,
            0.19
        ]
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

            load_soi(
                soi
            )

            st.rerun()

    with col3:

        if st.button(
            "🗑️",
            key=f"delete_soi_{idx}",
            use_container_width=True
        ):

            delete_soi(
                idx
            )

            st.rerun()


# =====================================================
# MAIN RENDERER
# =====================================================

def render_soi_registry():

    ensure_soi_state()

    with st.expander(
        "📚 Saved SOIs",
        expanded=False
    ):

        if not st.session_state.saved_sois:

            st.info(
                "No saved SOIs."
            )

            return

        render_loaded_soi_status()

        for idx, soi in enumerate(
            st.session_state.saved_sois
        ):

            render_saved_soi_row(
                soi,
                idx
            )