## --------------------------------------------------------------------------------------
## lenses.py
## --------------------------------------------------------------------------------------

import streamlit as st


def render_lenses(
    dataset,
    working_df
):

    dimensions = (
        dataset["metrics"]
        +
        dataset["selected_indicators"]
    )

    indicators = (
        dataset["selected_indicators"]
    )

    active_lens = "None"

    params = {}

    max_n = max(
        len(working_df),
        1
    )

    default_n = min(
        5,
        max_n
    )

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
                "Indicator Dominance"
            ],
            key="active_lens"
        )

        if (
            "active_soi_name"
            in st.session_state
        ):

            st.caption(
                f"Working on loaded SOI: "
                f"{st.session_state.active_soi_name}"
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
                    "TOPSIS",
                    "VIKOR",
                    "Reference Point"
                ],
                key="pref_method"
            )

            st.caption(
                "All preference methods currently use equal weights."
            )

            params["maximize"] = st.multiselect(
                "Metrics to Maximize",
                dimensions,
                key="pref_maximize"
            )

            minimize_options = [
                d
                for d in dimensions
                if d not in params["maximize"]
            ]

            params["minimize"] = st.multiselect(
                "Metrics to Minimize",
                minimize_options,
                key="pref_minimize"
            )

            params["top_n"] = st.slider(
                "Top N Solutions",
                1,
                max_n,
                default_n,
                key="pref_top_n"
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
                ],
                key="div_method"
            )

            default_cluster_metrics = dimensions[
                :min(
                    2,
                    len(dimensions)
                )
            ]

            params["cluster_metrics"] = st.multiselect(
                "Metrics for Clustering",
                dimensions,
                default=default_cluster_metrics,
                key="div_cluster_metrics"
            )

            if params["method"] == "K-Medoids":

                params["k_mode"] = st.radio(
                    "Number of Clusters",
                    [
                        "Auto",
                        "Manual"
                    ],
                    horizontal=True,
                    key="div_k_mode"
                )

                if params["k_mode"] == "Manual":

                    max_k = max(
                        2,
                        min(
                            10,
                            max_n
                        )
                    )

                    default_k = min(
                        3,
                        max_k
                    )

                    params["k"] = st.slider(
                        "k Clusters",
                        2,
                        max_k,
                        default_k,
                        key="div_k"
                    )

                else:

                    st.caption(
                        "Auto mode selects k using silhouette score."
                    )
            elif params["method"] == "HDBSCAN":

                params["cluster_size_mode"] = st.radio(
                    "Cluster Size",
                    [
                        "Auto",
                        "Manual"
                    ],
                    horizontal=True,
                    key="div_hdbscan_size_mode"
                )

                if params["cluster_size_mode"] == "Auto":

                    params["granularity"] = st.selectbox(
                        "Cluster Granularity",
                        [
                            "Small (~5%)",
                            "Medium (~10%)",
                            "Large (~20%)"
                        ],
                        index=1,
                        key="div_hdbscan_granularity"
                    )

                else:

                    default_min_cluster_size = max(
                        2,
                        int(
                            0.10 * max_n
                        )
                    )

                    params["min_cluster_size"] = st.slider(
                        "Minimum Cluster Size",
                        2,
                        max(
                            2,
                            max_n
                        ),
                        default_min_cluster_size,
                        key="div_hdbscan_min_cluster_size"
                    )

                params["exclude_noise"] = st.checkbox(
                    "Exclude noise solutions",
                    value=True,
                    key="div_hdbscan_exclude_noise"
                )

            st.caption(
                "Diversity structures the current subset into clusters "
                "instead of applying a preference score."
            )

        # =====================================
        # Efficiency Lens
        # =====================================

        elif active_lens == "Efficiency":

            params["method"] = st.selectbox(
                "Efficiency Method",
                [
                    "Benefit/Cost Ratio",
                    "Normalized Ratio",
                    "Distance to Ideal",
                    "Composite Cost Ratio"
                ],
                key="eff_method"
            )
            params["benefit"] = st.selectbox(
                "Benefit Metric",
                dimensions,
                key="eff_benefit"
            )

            cost_options = [
                d
                for d in dimensions
                if d != params["benefit"]
            ]

            if len(cost_options) == 0:

                st.warning(
                    "At least two dimensions are required "
                    "for the Efficiency lens."
                )

                params["cost"] = params["benefit"]

            elif params["method"] == "Composite Cost Ratio":

                params["cost"] = st.multiselect(
                    "Cost Metrics",
                    cost_options,
                    default=cost_options[
                        :min(
                            2,
                            len(cost_options)
                        )
                    ],
                    key="eff_costs"
                )

            else:

                params["cost"] = st.selectbox(
                    "Cost Metric",
                    cost_options,
                    key="eff_cost"
                )

            params["top_n"] = st.slider(
                "Top N Solutions",
                1,
                max_n,
                default_n,
                key="eff_top_n"
            )

            st.caption(
                "Efficiency methods rank solutions "
                "by benefit-cost trade-off."
            )
        # =====================================
        # Indicator Dominance Lens
        # =====================================

        elif active_lens == "Indicator Dominance":

            if len(indicators) == 0:

                st.info(
                    "No indicators are currently selected. "
                    "Enable indicators in Data Enrichment first."
                )

                params["maximize"] = []
                params["minimize"] = []
                params["top_n"] = default_n

            else:

                params["maximize"] = st.multiselect(
                    "Indicators to Maximize",
                    indicators,
                    key="domain_maximize"
                )

                minimize_options = [
                    d
                    for d in indicators
                    if d not in params["maximize"]
                ]

                params["minimize"] = st.multiselect(
                    "Indicators to Minimize",
                    minimize_options,
                    key="domain_minimize"
                )

                params["top_n"] = st.slider(
                    "Top N per Indicator",
                    1,
                    max_n,
                    default_n,
                    key="domain_top_n"
                )

                st.caption(
                    "Indicator Dominance identifies solutions that repeatedly "
                    "appear among the best candidates for selected indicators."
                )