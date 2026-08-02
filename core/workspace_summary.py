import streamlit as st


def render_summary(
    df,
    dataset
):

    with st.expander(
        "📊 Dataset Summary",
        expanded=False
    ):

        c1, c2, c3 = st.columns(3)

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

        st.caption(
            f"Decision-variable prefix: "
            f"{dataset['config'].get('var_prefix')}"
        )
        if st.button(
            "🔄 Reset Exploration",
            use_container_width=True
        ):

            keys_to_keep = []

            for key in list(
                st.session_state.keys()
            ):

                if key not in keys_to_keep:

                    del st.session_state[key]

            st.rerun()
        st.download_button(
            label="⬇️ Export Current Subset",
            data=df.to_csv(
                index=False
            ),
            file_name=
                "current_subset.csv",
            mime="text/csv",
            use_container_width=True
        )
