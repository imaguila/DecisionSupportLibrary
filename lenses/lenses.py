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
            "Select an analytical lens",
            [
                "None",
                "Preference",
                "Diversity",
                "Efficiency",
                "Domain-Specific"
            ],
            key="active_lens"
        )

        if active_lens != "None":

            st.markdown(
                f"""
                <div style="
                    color:#E63946;
                    font-size:12px;
                    font-weight:600;
                    text-align:center;
                    margin:0.3rem 0 0.8rem 0;
                ">
                ───── {active_lens} lens ─────
                </div>
                """,
                unsafe_allow_html=True
            )


        # =====================================
        # Preference Lens
        # =====================================

        if active_lens == "Preference":
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
                len(dataset["df"]),
                min(5, len(dataset["df"]))
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
        # =====================================
        # SAVE SOI
        # =====================================

        if "saved_sois" not in st.session_state:

            st.session_state.saved_sois = []

        if active_lens != "None":

            st.markdown("---")

            default_name = (
                f"{active_lens} "
                f"#{len(st.session_state.saved_sois)+1}"
            )

            soi_name = st.text_input(
                "Name",
                value=default_name,
                key="soi_name"
            )

            if st.button(
                "💾 Save Current Set",
                use_container_width=True
            ):

                st.session_state.pending_save_soi = {
                    "name": soi_name,
                    "lens": active_lens,
                    "params": params
                }
    return active_lens, params