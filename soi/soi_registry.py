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

    if "active_soi_metadata" in st.session_state:

        del st.session_state[
            "active_soi_metadata"
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
        "active_soi_metadata"
    ] = {
        "lens": soi.get(
            "lens"
        ),
        "method": soi.get(
            "method"
        ),
        "group": soi.get(
            "group"
        ),
        "group_column": soi.get(
            "group_column"
        ),
        "source_size": soi.get(
            "source_size"
        ),
        "soi_size": soi.get(
            "soi_size"
        ),
        "created_at": soi.get(
            "created_at"
        ),
        "params": soi.get(
            "params",
            {}
        )
    }

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
# RENDER HELPERS
# =====================================================

def render_loaded_soi_status():

    if not has_loaded_soi():

        return

    st.success(
        f"Active SOI: "
        f"{st.session_state.active_soi_name} "
        f"({len(st.session_state.active_soi_ids)} solutions)"
    )

    metadata = st.session_state.get(
        "active_soi_metadata",
        {}
    )

    if metadata:

        lens = metadata.get(
            "lens"
        )

        method = metadata.get(
            "method"
        )

        group = metadata.get(
            "group"
        )

        if lens or method:

            label = lens or "Unknown lens"

            if method:

                label = (
                    f"{label} / {method}"
                )

            st.caption(
                label
            )

        if group:

            st.caption(
                f"Group: {group}"
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


def build_soi_main_label(
    soi
):

    name = soi.get(
        "name",
        "Unnamed SOI"
    )

    size = len(
        soi.get(
            "ids",
            []
        )
    )

    lens = soi.get(
        "lens",
        "Unknown"
    )

    method = soi.get(
        "method"
    )

    if method:

        return (
            f"{name} "
            f"[{size}] · "
            f"{lens} / {method}"
        )

    return (
        f"{name} "
        f"[{size}] · "
        f"{lens}"
    )


def render_soi_details(
    soi,
    idx
):

    with st.expander(
        "Details",
        expanded=False
    ):

        st.write(
            {
                "lens": soi.get(
                    "lens"
                ),
                "method": soi.get(
                    "method"
                ),
                "group": soi.get(
                    "group"
                ),
                "group_column": soi.get(
                    "group_column"
                ),
                "source_size": soi.get(
                    "source_size"
                ),
                "soi_size": soi.get(
                    "soi_size",
                    len(
                        soi.get(
                            "ids",
                            []
                        )
                    )
                ),
                "created_at": soi.get(
                    "created_at"
                ),
                "params": soi.get(
                    "params",
                    {}
                )
            }
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
            build_soi_main_label(
                soi
            )
        )

        group_label = soi.get(
            "group"
        )

        if group_label:

            st.caption(
                f"Group: {group_label}"
            )

        created_at = soi.get(
            "created_at"
        )

        if created_at:

            st.caption(
                f"Created: {created_at}"
            )

        render_soi_details(
            soi,
            idx
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