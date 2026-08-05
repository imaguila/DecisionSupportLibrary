## --------------------------------------------------------------------------------------
## core/workspace_summary.py
## --------------------------------------------------------------------------------------

import streamlit as st

from core.workspace_dataset import (
    render_dataset_table
)
from soi.soi_registry import(
    render_soi_tab
)


# =====================================================
# DERIVED / LENS COLUMNS
# =====================================================

def get_lens_columns(
    df
):

    lens_prefixes = [
        "preference_",
        "efficiency_",
        "diversity_",
        "domain_",
        "indicator_",
        "consensus_"
    ]

    lens_columns = [
        col
        for col in df.columns
        if any(
            col.startswith(
                prefix
            )
            for prefix in lens_prefixes
        )
    ]

    structural_columns = [
        col
        for col in [
            "cluster",
            "cluster_str",
            "group_label",
            "group_base",
            "highlight"
        ]
        if col in df.columns
    ]

    return (
        structural_columns
        +
        lens_columns
    )


# =====================================================
# SUMMARY METRICS
# =====================================================

def render_summary_metrics(
    df,
    dataset
):

    c1, c2, c3, c4 = st.columns(
        4
    )

    with c1:

        st.metric(
            "Solutions",
            len(df)
        )

    with c2:

        st.metric(
            "Attributes",
            len(df.columns)
        )

    with c3:

        st.metric(
            "Decision Variables",
            len(
                dataset[
                    "decision_variables"
                ]
            )
        )

    with c4:

        css_status = (
            "Active"
            if st.session_state.get(
                "css_enabled",
                False
            )
            else "Inactive"
        )

        st.metric(
            "CSS",
            css_status
        )


def render_lens_summary(
    df
):

    lens_columns = get_lens_columns(
        df
    )

    if len(lens_columns) == 0:

        st.caption(
            "No derived lens columns in the current set."
        )

        return

    st.caption(
        "Derived columns: "
        +
        ", ".join(
            lens_columns
        )
    )


#def render_export_button(
#    df ):

#    st.download_button(
#        label="⬇️ Export Current Set",
#        data=df.to_csv(
#            index=False
#        ),
#        file_name="current_set.csv",
#        mime="text/csv",
#        use_container_width=True
#    )


def get_summary_label():

    if st.session_state.get(
        "css_enabled",
        False
    ):

        return "Dataset Summary / Current CSS"

    return "Dataset Summary / Current Set"


# =====================================================
# MAIN RENDERER
# =====================================================

def render_summary(df, dataset):
    if df is None:
        st.error(
            "Dataset summary cannot be rendered "
            "because the current dataframe is empty." )
        return

    label = get_summary_label()

    with st.expander(f"📊 {label}", expanded=False):
        tab_overview, tab_current, tab_saved_soi = st.tabs(
            [
                "**| Overview |**",
                "**| Current Set |**",
                "**| Saved SOIs |**"
            ]
        )

        with tab_overview:
            render_summary_metrics(df, dataset)
            st.caption(
                f"Decision-variable prefix: "
                f"{dataset['config'].get('var_prefix')}" )
            render_lens_summary(df)
        with tab_current:
            render_dataset_table(df, dataset)
        with tab_saved_soi:
            render_soi_tab()
        