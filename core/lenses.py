import streamlit as st

def render_lenses(dataset):

    dimensions = (
        dataset["metrics"]  +  dataset["selected_indicators"]
    )

    active_lens = "None"
    params = {}

    with st.sidebar.expander(
        "🧭 Analytical Lenses",
        expanded=False
    ):
        st.markdown(
            "<span style='color: #0066CC; font-weight: bold; font-size: 18px; font-family: sans-serif;'>"
            "Lens"
            "</span>", 
            unsafe_allow_html=True
        )
        active_lens = st.selectbox(
            #"Lens",
       #     "",
            [
                "None",
                "Preference",
                "Diversity",
                "Efficiency",
                "Domain-Specific"
            ]
        )

        # =====================================
        # Preference Lens
        # =====================================

        if active_lens == "Preference":
            st.markdown(
                "<span style='color: #E63946; font-weight: bold; font-size: 18px; font-family: sans-serif;'>"
                " Scoring Method"
                "</span>", 
                unsafe_allow_html=True
            )
            params["method"] = st.selectbox(
                "Scoring Method",
                [
                    "Weighted Sum",
                    "TOPSIS"
                ]
            )
            params["maximize"] = st.multiselect(
                "Metrics to Maximize",
                dimensions
            )

            params["minimize"] = st.multiselect(
                "Metrics to Minimize",
                dimensions
            )



            params["top_n"] = st.slider(
                "Top N Solutions",
                1,
                100,
                20
            )

        # =====================================
        # Diversity Lens
        # =====================================

        elif active_lens == "Diversity":

            params["method"] = st.selectbox(
                "Clustering Method",
                [
                    "K-Medoids",
                    "HDBSCAN"
                ]
            )

            params["target_size"] = st.slider(
                "Target Subset Size",
                1,
                100,
                20
            )

        # =====================================
        # Efficiency Lens
        # =====================================

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
                "Top N Solutions",
                1,
                100,
                20
            )

        # =====================================
        # Domain Lens
        # =====================================

        elif active_lens == "Domain-Specific":

            params["indicators"] = st.multiselect(
                "Indicators",
                dataset["selected_indicators"]
            )

            params["top_n"] = st.slider(
                "Top N Solutions",
                1,
                100,
                20
            )

    return active_lens, params