import streamlit as st
import pandas as pd

from config import CASES
from plugins import PLUGIN_REGISTRY

from core.enrichment import (
    detect_available_indicators,
    apply_enrichment
)


# =====================================================
# HELPERS
# =====================================================

def detect_decision_variables(
    df,
    prefix
):

    return [
        c
        for c in df.columns
        if c.startswith(prefix)
    ]


def build_dataset(
    df,
    cfg
):
    plugin = None
    plugin_name = cfg.get(
        "plugin"
    )
    if plugin_name:
        plugin_class = (
            PLUGIN_REGISTRY.get(
                plugin_name
            )
        )
        if plugin_class:
            plugin = plugin_class(
                var_prefix=cfg.get(
                    "var_prefix",
                    "x_"
                )
            )

    # =================================================
    # OBJECTIVES
    # =================================================

    all_metrics = cfg.get(
        "metrics",
        []
    )

    # Auto-detect objectives for uploaded CSVs

    if not all_metrics:
        var_prefix = cfg.get(
            "var_prefix",
            "x_"
        )
        excluded = set(
            cfg.get(
                "exclude_cols",
                []
            )
        )

        all_metrics = []

        for col in df.columns:

            if col.startswith(
                var_prefix
            ):
                continue

            if col in excluded:
                continue
            if col in [
                "id",
                "highlight",
                "label",
                "cluster",
                "score"
            ]:
                continue

            if pd.api.types.is_numeric_dtype(
                df[col]
            ):
                all_metrics.append(col)

    # =================================================
    # OBJECTIVES
    # =================================================

    selected_metrics = st.multiselect(
        "Optimization Objectives",
        all_metrics,
        default=all_metrics
    )

    # =================================================
    # ENRICHMENT
    # =================================================

    selected_indicators = []
    if plugin:
        available_indicators = []
        requirements = (
            plugin.requirements()
        )

        for indicator, reqs in requirements.items():

            if all(
                metric in selected_metrics
                for metric in reqs
            ):

                available_indicators.append(
                    indicator
                )

        with st.sidebar.expander(
            "⚙️ Data Enrichment",
            expanded=False
        ):

            selected_indicators = (
                st.multiselect(
                    "Indicators",
                    sorted(
                        available_indicators
                    ),
                    default=[
                        i
                        for i in cfg.get(
                            "default_indicators",
                            []
                        )
                        if i in available_indicators
                    ]
                )
            )

        df = apply_enrichment(
            df,
            plugin,
            selected_indicators
        )

    # =================================================
    # DATASET OBJECT
    # =================================================

    dataset = {

        "df": df,

        "config": cfg,

        "plugin": plugin,

        "metrics":
            selected_metrics,

        "selected_indicators":
            selected_indicators,

        "decision_variables":
            detect_decision_variables(
                df,
                cfg.get(
                    "var_prefix",
                    "x_"
                )
            )
    }

    return dataset


# =====================================================
# MAIN PANEL
# =====================================================

def render_input_panel():

    with st.sidebar.expander("🏷️ Input and Preparation", expanded=True):
        mode = st.radio(
            "Data Source",
            [
                "Domain Configuration",
                "Upload Enriched CSV"
            ],
            horizontal=True,
            help="""💡Choose how the decision space will be loaded.
            •Domain Configuration: dataset + configuration + plugin.
            •Enriched Dataset: self-contained dataset with no plugin
            """
        )
        if mode == "Domain Configuration":
            st.caption(
                "💡 Load a predefined domain package including a Pareto front, "
                "optimization objectives, decision-variable definitions, default indicators, "
                "and an optional domain plugin for enrichment."
            )
        else:
            st.caption(
                "💡 Upload a self-contained Pareto-front dataset. Decision variables are "
                "identified using the specified prefix (e.g., req_, var_, x_). All remaining "
                "numeric attributes become available as analysis dimensions."
            )

        # ==========================================
        # BUILT-IN DATASETS
        # ==========================================

        if mode == "Domain Configuration":
            dataset_names = list(
                CASES.keys()
            )

            dataset_name = (
                st.selectbox(
                    "Domain Configuration",
                    dataset_names,
                    help=CASES[
                        dataset_names[0]
                    ].get(
                        "help",
                        "No information available."
                    )
                )
            )

            cfg = CASES[
                dataset_name
            ]

            df = pd.read_csv(
                cfg["path_sol"]
            )

            df.reset_index(
                drop=True,
                inplace=True
            )

            df["id"] = range(
                len(df)
            )
            return build_dataset(
                df,
                cfg
            )

        # ==========================================
        # UPLOAD CSV
        # ==========================================

        uploaded_file = st.file_uploader(
            "Upload CSV",
            type=["csv"]
        )

        if uploaded_file:

            var_prefix = (
                st.text_input(
                    "Decision-variable prefix",
                    value="var_",
                    help=(
                        "Prefix used to identify "
                        "decision variables "
                        "(e.g. req_, var_, x_, "
                        "feature_, design_)."
                    )
                )
            )

            df = pd.read_csv(
                uploaded_file
            )
            df.reset_index(
                drop=True,
                inplace=True
            )

            df["id"] = range(
                len(df)
            )
            cfg = {
                "plugin": None,
                "metrics": [],
                "var_prefix":
                    var_prefix,
                "exclude_cols": [],
                "default_indicators":
                    []
            }

            return build_dataset(
                df,
                cfg
            )

    return None