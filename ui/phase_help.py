## --------------------------------------------------------------------------------------
## ui/phase_help.py
## --------------------------------------------------------------------------------------

import streamlit as st


# =====================================================
# PHASE HELP TEXTS
# =====================================================

PHASE_HELP = {
    "input": (
        "Load or define the decision dataset and domain configuration. "
        "This phase establishes the base decision space."
    ),

    "enrichment": (
        "Add derived indicators to the original dataset. "
        "These indicators enrich the decision space with additional views."
    ),

    "framing": (
        "Filter the decision space according to the current analytical context. "
        "Framing reduces the dataset before applying lenses or selecting a CSS."
    ),

    "workspace_controls": (
        "Create and manage decision-space maps. "
        "Maps visualize the current decision set, SOI, or CSS."
    ),

    "soi": (
        "Generate or load a Solution of Interest. "
        "A SOI is a candidate subset produced by a lens, a saved set, "
        "a consensus of saved SOIs, or the exploratory current set."
    ),

    "saved_sois": (
        "Review, load, or delete saved Solutions of Interest. "
        "Saved SOIs store solution IDs and traceability metadata."
    ),

    "css": (
        "Lock the current decision set as a Candidate Solution Set, "
        "or manually select specific solutions for detailed comparison."
    ),

    "summary": (
        "Summarize the current decision set or CSS. "
        "This section shows size, attributes, decision variables, "
        "derived columns, export options, and the current data table."
    ),

    "maps": (
        "Explore the current decision set or CSS visually. "
        "Maps reveal trade-offs, clusters, groups, scores, and highlighted candidates."
    ),

    "comparison": (
        "Compare selected candidate solutions in detail using radar profiles "
        "and decision-variable composition views."
    )
}

# =====================================================
# HELP ACCESS
# =====================================================

def get_phase_help(
    phase_key
):

    return PHASE_HELP.get(
        phase_key,
        ""
    )


def get_panel_state_key(
    key
):

    return (
        f"{key}_open"
    )


def ensure_panel_state(
    key,
    expanded
):

    state_key = get_panel_state_key(
        key
    )

    if state_key not in st.session_state:

        st.session_state[
            state_key
        ] = expanded

    return state_key


def toggle_panel_state(
    state_key
):

    st.session_state[
        state_key
    ] = not st.session_state[
        state_key
    ]

# =====================================================
# SIDEBAR PHASE PANEL
# =====================================================

def render_sidebar_phase_panel_header(
    title,
    phase_key,
    key,
    expanded=False
):

    state_key = ensure_panel_state(
        key,
        expanded
    )

    is_open = st.session_state[
        state_key
    ]

    arrow = (
        "▾"
        if is_open
        else "▸"
    )

    help_text = get_phase_help(
        phase_key
    )

    col_title, col_help = st.sidebar.columns(
        [
            0.88,
            0.12
        ]
    )

    with col_title:

        if st.button(
            f"{arrow} {title}",
            key=f"{key}_toggle",
            use_container_width=True
        ):

            toggle_panel_state(
                state_key
            )

            st.rerun()

    with col_help:

        if not is_open:

            if st.button(
                "ⓘ",
                key=f"{key}_help",
                help=help_text,
                use_container_width=True
            ):

                pass

        else:

            st.empty()

    return is_open


def sidebar_phase_container(
    title,
    phase_key,
    key,
    expanded=False
):

    is_open = render_sidebar_phase_panel_header(
        title,
        phase_key,
        key,
        expanded
    )

    if not is_open:

        return None

    return st.sidebar.container(
        border=True
    )

# =====================================================
# MAIN AREA PHASE PANEL
# =====================================================

def render_main_phase_panel_header(
    title,
    phase_key,
    key,
    expanded=False
):

    state_key = ensure_panel_state(
        key,
        expanded
    )

    is_open = st.session_state[
        state_key
    ]

    arrow = (
        "▾"
        if is_open
        else "▸"
    )

    help_text = get_phase_help(
        phase_key
    )

    col_title, col_help = st.columns(
        [
            0.94,
            0.06
        ]
    )

    with col_title:

        if st.button(
            f"{arrow} {title}",
            key=f"{key}_toggle",
            use_container_width=True
        ):

            toggle_panel_state(
                state_key
            )

            st.rerun()

    with col_help:

        if not is_open:

            if st.button(
                "ⓘ",
                key=f"{key}_help",
                help=help_text,
                use_container_width=True
            ):

                pass

        else:

            st.empty()

    return is_open


def main_phase_container(
    title,
    phase_key,
    key,
    expanded=False
):

    is_open = render_main_phase_panel_header(
        title,
        phase_key,
        key,
        expanded
    )

    if not is_open:

        return None

    return st.container(
        border=True
    )

# =====================================================
# BACKWARD COMPATIBILITY
# =====================================================

def render_phase_title(
    title,
    phase_key,
    sidebar=False
):

    if sidebar:

        return sidebar_phase_container(
            title,
            phase_key,
            key=f"{phase_key}_phase_title",
            expanded=False
        )

    return main_phase_container(
        title,
        phase_key,
        key=f"{phase_key}_phase_title",
        expanded=False
    )