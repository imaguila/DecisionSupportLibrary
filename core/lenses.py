import streamlit as st


def render_lenses(
    dataset
):

    dimensions = (
        dataset["metrics"]
        +
        dataset["selected_indicators"]
    )

    with st.sidebar.expander(
        "🧭 Analytical Lenses",
        expanded=False
    ):

        active_lens = st.selectbox(
            "Lens",
            [
                "None",
                "Preference",
                "Diversity",
                "Efficiency",
                "Domain-Specific"
            ]
        )

        params = {}

        # ======================================
        # Preference Lens
        # ======================================

        if active_lens == "Preference":

            params["maximize"] = st.multiselect(
                "Maximize",
                dimensions
            )

            params["minimize"] = st.multiselect(
                "Minimize",
                dimensions
            )

            params["method"] = st.selectbox(
                "Method",
                [
                    "Weighted Sum",
                    "TOPSIS"
                ]
            )

            params["top_n"] = st.slider(
                "Top N",
                1,
                100,
                20
            )

        # ======================================
        # Diversity Lens
        # ======================================

        elif active_lens == "Diversity":

            params["method"] = st.selectbox(
                "Clustering",
                [
                    "K-Medoids",
                    "HDBSCAN"
                ]
            )

            params["top_n"] = st.slider(
                "Target Size",
                1,
                100,
                20
            )

        # ======================================
        # Efficiency Lens
        # ======================================

        elif active_lens == "Efficiency":

            params["benefit"] = st.selectbox(
                "Benefit Metric",
                dimensions
            )

            params["cost"] = st.selectbox(
                "Cost Metric",
                dimensions
            )

            params["top_n"] = st.slider(
                "Top N",
                1,
                100,
                20
            )

        # ======================================
        # Domain Lens
        # ======================================

        elif active_lens == "Domain-Specific":

            params["indicators"] = st.multiselect(
                "Indicators",
                dataset[
                    "selected_indicators"
                ]
            )

            params["top_n"] = st.slider(
                "Top N",
                1,
                100,
                20
            )

    return active_lens, params