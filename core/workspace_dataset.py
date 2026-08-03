## --------------------------------------------------------------------------------------
## workspace_dataset.py


import streamlit as st


def render_dataset_preview(
    df,
    dataset
):

    with st.expander(
        f"📋 Current Dataset "
        f"(prefix: "
        f"{dataset['config'].get('var_prefix')})",
        expanded=False
    ):
        var_prefix = dataset["config"].get(
            "var_prefix",
            "x_"
        )
        objective_cols = dataset["metrics"]
        indicator_cols = dataset[
            "selected_indicators"
        ]
        decision_cols = [
            c
            for c in df.columns
            if c.startswith(
                var_prefix
            )
        ]
        other_cols = [
            c
            for c in df.columns
            if (
                c not in objective_cols
                and c not in indicator_cols
                and c not in decision_cols
                and c != "id"
            )
        ]

        ordered_cols = (
            ["id"]
            +
            objective_cols
            +
            indicator_cols
            +
            other_cols
            +
            decision_cols
        )

        ordered_cols = [
            c
            for c in ordered_cols
            if c in df.columns
        ]

        st.dataframe(
            df[ordered_cols],
            use_container_width=True,
            height=500,
            hide_index=True
        )
