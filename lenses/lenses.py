## --------------------------------------------------------------------------------------
## lenses.py
## --------------------------------------------------------------------------------------

import streamlit as st

from lenses.lens_registry import (
    get_lens_names,
    get_lens_module
)


# =====================================================
# SESSION HELPERS
# =====================================================

def ensure_soi_state():

    if "saved_sois" not in st.session_state:

        st.session_state.saved_sois = []


def reset_soi_name_if_lens_changed(
    active_lens
):

    default_name = (
        f"{active_lens} "
        f"#{len(st.session_state.saved_sois) + 1}"
    )

    if (
        st.session_state.get(
            "soi_name_lens"
        )
        != active_lens
    ):

        st.session_state[
            "soi_name"
        ] = default_name

        st.session_state[
            "soi_name_lens"
        ] = active_lens


# =====================================================
# HEADER
# =====================================================

def render_lens_header(
    active_lens
):

    if (
        "active_soi_name"
        in st.session_state
    ):

        st.caption(
            f"Working on loaded SOI: "
            f"{st.session_state.active_soi_name}"
        )

    if active_lens != "None":

        st.markdown(
            f"""
            <div style="
                color:#E63946;
                font-size:12px;
                font-weight:600;
                text-align:center;
                margin:0.3rem 0 0.8rem 0;
            ">
            ───── {active_lens} lens ─────
            </div>
            """,
            unsafe_allow_html=True
        )


# =====================================================
# LENS PARAMETERS
# =====================================================

def render_active_lens_params(
    active_lens,
    dataset,
    working_df
):

    if active_lens == "None":

        return {}

    lens_module = get_lens_module(
        active_lens
    )

    if lens_module is None:

        st.warning(
            f"No module registered for lens: {active_lens}"
        )

        return {}

    if not hasattr(
        lens_module,
        "render_params"
    ):

        st.warning(
            f"Lens module '{active_lens}' does not define render_params()."
        )

        return {}

    return lens_module.render_params(
        dataset,
        working_df
    )


# =====================================================
# SAVE SOI
# =====================================================

def render_save_soi_controls(
    active_lens,
    params
):

    if active_lens == "None":

        return

    st.markdown("---")

    reset_soi_name_if_lens_changed(
        active_lens
    )

    soi_name = st.text_input(
        "Name",
        key="soi_name"
    )

    if st.button(
        "💾 Save Current Set",
        use_container_width=True,
        key="save_current_soi"
    ):

        st.session_state.pending_save_soi = {
            "name": soi_name,
            "lens": active_lens,
            "params": params
        }


# =====================================================
# MAIN PANEL
# =====================================================

def render_lens_panel(
    dataset,
    working_df
):

    ensure_soi_state()

    params = {}

    with st.sidebar.expander(
        "🧭 Solution of interest",
        expanded=False
    ):

        active_lens = st.selectbox(
            "Select an analytical lens",
            get_lens_names(),
            key="active_lens"
        )

        render_lens_header(
            active_lens
        )

        params = render_active_lens_params(
            active_lens,
            dataset,
            working_df
        )

        render_save_soi_controls(
            active_lens,
            params
        )

        feedback_placeholder = st.empty()

    return active_lens, params, feedback_placeholder