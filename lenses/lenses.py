import streamlit as st

def render_lenses(dataset):

    dimensions = (
        dataset["metrics"]  +  dataset["selected_indicators"]
    )

    active_lens = "None"
    params = {}

    with st.sidebar.expander(
        "🧭 Solution of interest",
        expanded=False
    ):
        active_lens = st.selectbox(
            "Analytical Lens Selected",
            [
                "None",
                "Preference",
                "Diversity",
                "Efficiency",
                "Domain-Specific"
            ],
            #label_visibility="collapsed"
        )

        if active_lens != "None":

            st.markdown(
                f"""
                <div style="
                    background-color:#FFE5E5;
                    color:#B00020;
                    border-left:4px solid #E63946;
                    padding:0.5rem;
                    border-radius:0.3rem;
                    font-weight:bold;
                    margin-bottom:0.75rem;
                ">
                    ⭐ Active SOI: {active_lens}
                </div>
                """,
                unsafe_allow_html=True
            )


        # =====================================
        # Preference Lens
        # =====================================

        if active_lens == "Preference":
           # st.markdown(
           #     "<span style='color: #E63946; font-weight: bold; font-size: 18px; font-family: sans-serif;'>"
           #     " Scoring Method"
           #     "</span>", 
           #     unsafe_allow_html=True
           # )
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