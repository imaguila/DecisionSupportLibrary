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

        st.dataframe(
            df,
            use_container_width=True,
            height=500
        )