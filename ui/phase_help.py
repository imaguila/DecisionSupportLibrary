"""
Phase Help Module.

Provides documentation text dictionaries and Streamlit popover UI helper
components for displaying phase-specific contextual guidance across the application.
"""

from typing import Dict, Optional

import streamlit as st

# =====================================================
# PHASE HELP TEXTS
# =====================================================

PHASE_HELP: Dict[str, str] = {
    "input": (
        "Load the base decision space.\n\n"
        "**1. Domain Configuration**\n\n"
        "Use this option when you want to load a predefined case already configured in the library.\n\n"
        "A domain configuration usually provides:\n"
        "- the solution dataset\n"
        "- the default optimization objectives\n"
        "- the decision-variable prefix\n"
        "- optional plugin logic\n"
        "- optional default indicators\n\n"
        "This is the recommended option when the decision problem has a known structure.\n\n"
        "**2. Upload Enriched CSV**\n\n"
        "Use this option when you already have a standalone CSV.\n\n"
        "The uploaded CSV should contain:\n"
        "- one row per solution\n"
        "- numeric objective or indicator columns\n"
        "- decision-variable columns sharing a common prefix\n\n"
        "Examples of decision-variable prefixes:\n"
        "- `x_`\n"
        "- `var_`\n"
        "- `req_`\n"
        "- `feature_`\n"
        "- `design_`\n\n"
        "After loading the data, refine the Objective Column (optimization objectives) that define the base decision space.\n\n"
        "> **User Purpose:** Load the base Pareto-optimal alternatives to start transforming them into an interpretable decision space."
    ),
    "enrichment": (
        "The goal of this stage is to **expand the descriptive layer of the solutions** by adding domain-specific quality and semantic indicators.\n\n"
        "Available indicators are provided by the active domain plugin. The app checks "
        "which indicators can be computed from the currently selected base objectives.\n\n"
        "Only compatible indicators are shown. An indicator is compatible when all "
        "required input columns are available in the current dataset.\n\n"
        "Each indicator must also have its calculation logic defined in the plugin. "
        "If the plugin does not define how an indicator is computed, the app cannot "
        "generate that indicator.\n\n"
        "Derived indicators enrich the decision space with additional analytical views, "
        "such as:\n"
        "- productivity\n"
        "- scope\n"
        "- quality\n"
        "- efficiency\n"
        "- domain-specific measures\n\n"
        "> **User Purpose:** Uncover implicit properties in solutions to project, filter, and compare the decision space under richer analytical perspectives."
    ),
    "framing": (
        "The goal of this stage is to **restrict the global decision space to current operational conditions**.\n\n"
        "Use constraints in this section to delimit the active set by applying:\n"
        "- Maximum effort (budget) thresholds.\n"
        "- Risk limits or minimum productivity/scope requirements.\n\n"
        "> **User Purpose:** Reduce analytical complexity by isolating only those solutions that are viable under the current strategic context before applying analytical lenses."
    ),
    "workspace_controls": (
        "Create and manage decision-space maps.\n\n"
        "Maps visualize the current decision set, SOI, or CSS using selected objectives and indicators.\n\n"
        "The goal of Maps is to **project and visualize alternatives across multiple dimensions simultaneously**.\n\n"
        "Configure the axes (X, Y) and marker size to inspect how objectives and derived indicators behave across the active solution set.\n\n"
        "> **User Purpose:** Detect visual patterns, trade-offs, and spatial distributions without committing to a single ranking upfront."
    ),
    "soi": (
        "Generate or load a Solution of Interest.\n\n"
        "A SOI is a candidate subset of solutions. It can come from:\n"
        "- an analytical lens\n"
        "- a saved SOI\n"
        "- a consensus of saved SOIs\n"
        "- the exploratory current set\n\n"
        "The goal of this stage is to **identify Solutions of Interest (SOIs)**: sub-sets with strategic coherence identified under a specific analytical perspective (Lens).\n\n"
        "Rather than evaluating isolated solutions, apply different Analytical Lenses:\n"
        "- **Preference (MCDA):** Discover top-N alternatives based on TOPSIS or Weighted Sum.\n"
        "- **Diversity:** Group structurally representative solutions using clustering (K-Medoids, HDBSCAN).\n"
        "- **Efficiency:** Identify solutions offering the best benefit-cost trade-offs.\n"
        "- **Dominance:** Highlight alternatives that repeatedly excel across multiple quality indicators.\n\n"
        "> **User Purpose:** Extract latent strategic insights and patterns from the decision space using intermediate analytical units (SOIs).\n\n"
        "Examples of Lens include:\n"
        "- a cluster from Diversity\n"
        "- a Top-N set from Preference\n"
        "- an efficient subset\n"
        "- a non-dominated subset\n"
        "- a manually saved current set"
    ),
    "saved_sois": (
        "Review, load, or delete saved Solutions of Interest.\n\n"
        "Saved SOIs store:\n"
        "- solution IDs\n"
        "- source lens\n"
        "- method\n"
        "- selected group\n"
        "- parameters\n"
        "- creation context\n\n"
        "Use saved SOIs to return to previous interesting subsets or combine them later."
    ),
    "css": (
        "Define the Candidate Solution Set.\n\n"
        "The CSS is the final subset that will be studied in detail.\n\n"
        "You can build it from:\n"
        "- the current decision set\n"
        "- the current SOI\n"
        "- a manual selection of specific solutions\n\n"
        "Once a CSS is active, it can be used for detailed visual comparison."
    ),
    "summary": (
        "Summarize the current decision set or CSS.\n\n"
        "This section shows:\n"
        "- number of solutions\n"
        "- number of attributes\n"
        "- number of decision variables\n"
        "- CSS status\n"
        "- derived columns\n"
        "- export options\n"
        "- the current data table"
    ),
    "maps": (
        "Explore the current decision set or CSS visually.\n\n"
        "Maps help reveal:\n"
        "- trade-offs\n"
        "- clusters\n"
        "- consensus groups\n"
        "- preference scores\n"
        "- efficiency scores\n"
        "- highlighted candidates"
    ),
    "comparison": (
        "Compare selected candidate solutions in detail.\n\n"
        "The detailed comparison includes:\n"
        "- radar profiles for objectives and indicators\n"
        "- decision-variable composition matrix\n"
        "- decision-variable distribution inside the CSS"
    ),
}


# =====================================================
# HELP ACCESS
# =====================================================


def get_phase_help(phase_key: str) -> str:
    """
    Retrieves the contextual help markdown text for a specified pipeline phase.

    Parameters
    ----------
    phase_key : str
        Key string identifying the pipeline phase.

    Returns
    -------
    str
        Markdown string containing phase documentation, or empty string if key is invalid.
    """
    if not isinstance(phase_key, str):
        return ""
    return PHASE_HELP.get(phase_key, "")


def get_help_text(phase_key: str) -> str:
    """
    Alias for `get_phase_help`.

    Parameters
    ----------
    phase_key : str
        Key string identifying the pipeline phase.

    Returns
    -------
    str
        Markdown string containing phase documentation.
    """
    return get_phase_help(phase_key)


# =====================================================
# HELP POPOVER COMPONENTS
# =====================================================


def render_help_icon(
    help_text: Optional[str],
    key: Optional[str] = None,
    label: str = "ⓘ",
) -> None:
    """
    Renders a Streamlit popover containing generic markdown help text.

    Parameters
    ----------
    help_text : Optional[str]
        Markdown content to render inside the popover.
    key : Optional[str], optional
        Optional widget key for Streamlit popover element, by default None.
    label : str, default="ⓘ"
        Popover button label string.
    """
    if not help_text:
        return

    popover_kwargs = {"label": label}
    if key is not None:
        popover_kwargs["key"] = key

    with st.popover(**popover_kwargs):
        st.markdown(help_text)


def render_phase_help_icon(
    phase_key: str,
    key: Optional[str] = None,
    label: str = "ⓘ",
) -> None:
    """
    Renders a Streamlit popover with contextual help text for a target pipeline phase.

    Parameters
    ----------
    phase_key : str
        Key string identifying the target phase.
    key : Optional[str], optional
        Optional widget key for Streamlit popover element.
        If None, a unique key is automatically generated using phase_key.
    label : str, default="ⓘ"
        Popover button label string.
    """
    help_text = get_phase_help(phase_key)
    if not help_text:
        return

    # Automatically generate a unique key if none is explicitly provided
    resolved_key = key if key is not None else f"help_phase_{phase_key}"

    render_help_icon(help_text, key=resolved_key, label=label)
    