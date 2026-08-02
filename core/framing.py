import streamlit as st
import pandas as pd


def apply_framing(dataset):

    df = dataset["df"].copy()

    dimensions = (
        dataset["metrics"]
        +
        dataset["selected_indicators"]
    )

    filtered_df = df.copy()

    with st.sidebar.expander(
        "🎛️ Context Framing",
        expanded=False
    ):

        # ----------------------------------
        # Reset framing
        # ----------------------------------

        if st.button(
            "🔄 Reset Framing",
            use_container_width=True
        ):
            framing_keys = [
                k
                for k in st.session_state.keys()
                if k.startswith("framing_")
            ]
            for key in framing_keys:
                del st.session_state[key]
            st.rerun()

        # ----------------------------------
        # Dimension filters
        # ----------------------------------

        for metric in dimensions:

            if metric not in filtered_df.columns:
                continue

            if not pd.api.types.is_numeric_dtype(
                filtered_df[metric]
            ):
                continue

            min_v = float(
                filtered_df[metric].min()
            )

            max_v = float(
                filtered_df[metric].max()
            )

            if min_v == max_v:
                continue

            selected_range = st.slider(
                metric,
                min_v,
                max_v,
                (min_v, max_v),
                key=f"framing_{metric}"
            )
            filtered_df = filtered_df[
                (
                    filtered_df[metric]
                    >= selected_range[0]
                )
                &
                (
                    filtered_df[metric]
                    <= selected_range[1]
                )
            ]

        # ----------------------------------
        # Framing summary
        # ----------------------------------

        total_solutions = len(df)
        remaining_solutions = len(
            filtered_df
        )
        ratio = (
            remaining_solutions
            /
            max(total_solutions, 1)
        )
        st.progress(ratio)
        st.metric(
            "Remaining Solutions",
            f"{remaining_solutions}/{total_solutions}"
        )
        st.caption(
            f"{ratio:.0%} of the decision space remains visible."
        )
    return filtered_df