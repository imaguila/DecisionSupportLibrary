## --------------------------------------------------------------------------------------
## ui/phase_help.py
## --------------------------------------------------------------------------------------

import html
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
        "These indicators enrich the decision space with additional views "
        "such as productivity, scope, quality, efficiency, or domain-specific measures."
    ),

    "framing": (
        "Filter the decision space according to the current analytical context. "
        "Framing reduces the dataset before applying lenses, SOI generation, "
        "CSS selection, or detailed comparison."
    ),

    "workspace_controls": (
        "Create and manage decision-space maps. "
        "Maps visualize the current decision set, SOI, or CSS using selected "
        "objectives and indicators."
    ),

    "soi": (
        "Generate or load a Solution of Interest. "
        "A SOI is a candidate subset produced by an analytical lens, "
        "a saved subset, a consensus of saved SOIs, or the exploratory current set."
    ),

    "saved_sois": (
        "Review, load, or delete saved Solutions of Interest. "
        "Saved SOIs store solution IDs and traceability metadata such as lens, "
        "method, group, parameters, and creation context."
    ),

    "css": (
        "Lock the current decision set as a Candidate Solution Set, "
        "or manually select specific solutions for detailed visual comparison. "
        "The CSS is the final subset studied in detail."
    ),

    "summary": (
        "Summarize the current decision set or CSS. "
        "This section shows size, attributes, decision variables, derived columns, "
        "export options, and the current data table."
    ),

    "maps": (
        "Explore the current decision set or CSS visually. "
        "Maps reveal structure, trade-offs, clusters, consensus groups, "
        "preference scores, and highlighted candidates."
    ),

    "comparison": (
        "Compare selected candidate solutions in detail using radar profiles "
        "for objectives and indicators, plus decision-variable composition views."
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


# =====================================================
# INLINE HELP ICON
# =====================================================

def render_phase_help_icon( phase_key ):

    help_text = get_phase_help(phase_key)

    if not help_text:
        return

    safe_help = html.escape(
        help_text
    )

    st.markdown(
        (
            "<div style='text-align:right;'>"
            "<span "
            f"title=\"{safe_help}\" "
            "style='"
            "cursor:help;"
            "color: #ffff00;"
            "font-size:2rem;"
            "line-height:0.5;"
            "'>"
            "✧"
            "</span>"
            "</div>"
        ),
        unsafe_allow_html=True
    )


# =====================================================
# COMPACT HELP ROW
# =====================================================

def render_phase_help_row(
    phase_key
):

    help_text = get_phase_help(
        phase_key
    )

    if not help_text:

        return

    safe_help = html.escape(
        help_text
    )

    st.markdown(
        (
            "<span "
            f"title=\"{safe_help}\" "
            "style='"
            "cursor:help;"
            "color:#6b7280;"
            "font-size:0.85rem;"
            "'>"
            "ⓘ Phase help"
            "</span>"
        ),
        unsafe_allow_html=True
    )


# =====================================================
# GENERIC TOOLTIP ICON
# =====================================================

def render_help_icon(
    help_text,
    key=None
):

    if not help_text:

        return

    button_key = (
        key
        if key is not None
        else "generic_help_icon"
    )

    if st.button(
        "ⓘ",
        key=button_key,
        help=help_text,
        use_container_width=True
    ):

        pass
