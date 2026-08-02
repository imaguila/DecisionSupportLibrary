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
        # Dimension filters
        # ----------------------------------

        for metric in dimensions:

            if metric not in df.columns:
                continue

            if not pd.api.types.is_numeric_dtype(
                df[metric]
            ):
                continue

            min_v = float(
                df[metric].min()
            )

            max_v = float(
                df[metric].max()
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

            # Si el slider está abierto completamente,
            # no aplicar ningún filtro.
            if (
                abs(selected_range[0] - min_v) < 1e-6
                and
                abs(selected_range[1] - max_v) < 1e-6
            ):
                continue

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

        st.markdown(
            f"""
            <div style="text-align:center">
                <div style="font-size:0.9rem;color:gray;">
                    Remaining Solutions
                </div>
                <div style="font-size:1.8rem;font-weight:bold;">
                    {remaining_solutions}/{total_solutions}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            f"{ratio:.0%} of the decision space is visible."
        )

        # ----------------------------------
        # Reset framing
        # ----------------------------------

        if st.button(
            "🔄 Reset Framing",
            use_container_width=True
        ):

            for key in list(
                st.session_state.keys()
            ):

                if key.startswith(
                    "framing_"
                ):

                    del st.session_state[key]

            st.rerun()

    return filtered_df