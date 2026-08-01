import streamlit as st
import pandas as pd

from config import CASES
from plugins import PLUGIN_REGISTRY
from enrichment import (
    detect_available_indicators,
    apply_enrichment
)


# =====================================================
# HELPERS
# =====================================================

def detect_decision_variables(df, prefix):

    return [
        c
        for c in df.columns
        if c.startswith(prefix)
    ]


def build_dataset(df, cfg):

    plugin = None

    plugin_name = cfg.get("plugin")

    if plugin_name:

        plugin_class = PLUGIN_REGISTRY.get(
            plugin_name
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
    # ----------------------------------
    # Automatic objective detection
    # for uploaded datasets
    # ----------------------------------

    if not all_metrics:

        var_prefix = cfg.get(
            "var_prefix",
            "x_"
        )

        all_metrics = []

        for col in df.columns:

            if col.startswith(var_prefix):
                continue

            if col in [
                "id",
                "highlight",
                "label",
                "score",
                "cluster"
            ]:
                continue

            if pd.api.types.is_numeric_dtype(
                df[col]
            ):
                all_metrics.append(col)
        st.sidebar.markdown(
            "### Optimization Objectives"
        )

    selected_metrics = (
        st.sidebar.multiselect(
            "Active objectives",
            all_metrics,
            default=all_metrics
        )
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

        st.sidebar.markdown(
            "### Data Enrichment"
        )

        selected_indicators = (
            st.sidebar.multiselect(
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

    st.sidebar.markdown(
        "## Input Data"
    )

    mode = st.sidebar.radio(
        "Source",
        [
            "Example Dataset",
            "Upload Enriched CSV"
        ]
    )

    # =================================================
    # BUILT-IN DATASETS
    # =================================================

    if mode == "Example Dataset":

        dataset_names = list(
            CASES.keys()
        )

        dataset_name = (
            st.sidebar.selectbox(
                "Dataset",
                dataset_names,
                help=CASES[
                    dataset_names[0]
                ].get(
                    "help",
                    "No information available."
                )
            )
        )

        cfg = CASES[dataset_name]

        df = pd.read_csv(
            cfg["path_sol"]
        )

        return build_dataset(
            df,
            cfg
        )

    # =================================================
    # UPLOAD ENRICHED CSV
    # =================================================

    uploaded_file = (
        st.sidebar.file_uploader(
            "Upload CSV",
            type=["csv"]
        )
    )

    if uploaded_file:

        var_prefix = (
            st.sidebar.text_input(
                "Decision-variable prefix",
                value="var_",
                help=(
                    "Prefix used to identify "
                    "decision variables "
                    "(e.g. req_, var_, x_, "
                    "feature_)."
                )
            )
        )

        df = pd.read_csv(
            uploaded_file
        )

        cfg = {

            "plugin": None,

            "metrics": [],

            "var_prefix":
                var_prefix,

            "default_indicators":
                []
        }

        return build_dataset(
            df,
            cfg
        )

    return None