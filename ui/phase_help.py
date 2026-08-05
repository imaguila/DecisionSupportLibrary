## --------------------------------------------------------------------------------------
## ui/phase_help.py
## --------------------------------------------------------------------------------------

import streamlit as st


# =====================================================
# PHASE HELP TEXTS
# =====================================================

PHASE_HELP = {
    "input": """
Load the base decision space.

**1. Domain Configuration**

Use this option when you want to load a predefined case already configured in the library.

A domain configuration usually provides:

- the solution dataset
- the default optimization objectives
- the decision-variable prefix
- optional plugin logic
- optional default indicators

This is the recommended option when the decision problem has a known structure.

**2. Upload Enriched CSV**

Use this option when you already have a standalone CSV.

The uploaded CSV should contain:

- one row per solution
- numeric objective or indicator columns
- decision-variable columns sharing a common prefix

Examples of decision-variable prefixes:

- `x_`
- `var_`
- `req_`
- `feature_`
- `design_`

After loading the data, refine the optimization objectives that define the base decision space.
""",

    "enrichment": """
Add derived indicators to the original dataset.

Indicators enrich the decision space with additional analytical views, such as:

- productivity
- scope
- quality
- efficiency
- domain-specific measures

These indicators can later be used in maps, lenses, SOI generation, CSS selection, and detailed comparison.
""",

    "framing": """
Filter the decision space according to the current analytical context.

Framing reduces the active dataset before applying:

- analytical lenses
- SOI generation
- CSS selection
- detailed comparison

Use this phase to restrict the decision space to the region that is currently relevant.
""",

    "workspace_controls": """
Create and manage decision-space maps.

Maps visualize the current decision set, SOI, or CSS using selected objectives and indicators.

Use this phase to decide which dimensions should be shown in each map.
""",

    "soi": """
Generate or load a Solution of Interest.

A SOI is a candidate subset of solutions. It can come from:

- an analytical lens
- a saved SOI
- a consensus of saved SOIs
- the exploratory current set

Examples of SOIs include:

- a cluster from Diversity
- a Top-N set from Preference
- an efficient subset
- a non-dominated subset
- a manually saved current set
""",

    "saved_sois": """
Review, load, or delete saved Solutions of Interest.

Saved SOIs store:

- solution IDs
- source lens
- method
- selected group
- parameters
- creation context

Use saved SOIs to return to previous interesting subsets or combine them later.
""",

    "css": """
Define the Candidate Solution Set.

The CSS is the final subset that will be studied in detail.

You can build it from:

- the current decision set
- the current SOI
- a manual selection of specific solutions

Once a CSS is active, it can be used for detailed visual comparison.
""",

    "summary": """
Summarize the current decision set or CSS.

This section shows:

- number of solutions
- number of attributes
- number of decision variables
- CSS status
- derived columns
- export options
- the current data table
""",

    "maps": """
Explore the current decision set or CSS visually.

Maps help reveal:

- trade-offs
- clusters
- consensus groups
- preference scores
- efficiency scores
- highlighted candidates
""",

    "comparison": """
Compare selected candidate solutions in detail.

The detailed comparison includes:

- radar profiles for objectives and indicators
- decision-variable composition matrix
- decision-variable distribution inside the CSS
"""
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


def get_help_text(
    phase_key
):

    return get_phase_help(
        phase_key
    )


# =====================================================
# GENERIC HELP POPOVER
# =====================================================

def render_help_icon(
    help_text,
    key=None,
    label="ⓘ"
):

    if not help_text:

        return

    with st.popover(
        label
    ):

        st.markdown(
            help_text
        )


# =====================================================
# PHASE HELP POPOVER
# =====================================================

def render_phase_help_icon(
    phase_key,
    key=None,
    label="ⓘ"
):

    help_text = get_phase_help(
        phase_key
    )

    if not help_text:

        return

    render_help_icon(
        help_text,
        key=key,
        label=label
    )