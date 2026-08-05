## --------------------------------------------------------------------------------------
## core/workspace_summary.py
## --------------------------------------------------------------------------------------

import streamlit as st

from core.workspace_dataset import (
    render_dataset_table
)


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

        return

    st.caption(
        "Derived columns: "
        +
        ", ".join(
            lens_columns
        )
    )


def render_export_button(
    df
):

    st.download_button(
        label="⬇️ Export Current Set",
        data=df.to_csv(
            index=False
        ),
        file_name="current_set.csv",
        mime="text/csv",
        use_container_width=True
        )
