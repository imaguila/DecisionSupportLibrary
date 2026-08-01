import streamlit as st
import pandas as pd

from config import CASES
from plugins import PLUGIN_REGISTRY
from enrichment import (
    detect_available_indicators,
    apply_enrichment,
)


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

        plugin_class = PLUGIN_REGISTRY.get(plugin_name)

        if plugin_class:

            plugin = plugin_class(
                var_prefix=cfg.get(
                    "var_prefix",
                    "x_"
                )
            )

    selected_indicators = []

    if plugin:

        available_indicators = (
            detect_available_indicators(
                plugin
            )
        )

        st.sidebar.markdown(
            "### Data Enrichment"
        )

        selected_indicators = (
            st.sidebar.multiselect(
                "Indicators",
                available_indicators,
                default=cfg.get(
                    "default_indicators",
                    []
                )
            )
        )

        df = apply_enrichment(
            df,
            plugin,
            selected_indicators
        )

    return {

        "df": df,

        "config": cfg,

        "plugin": plugin,

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

    # ==========================================
    # Example datasets
    # ==========================================

    if mode == "Example Dataset":

        dataset_names = list(
            CASES.keys()
        )

        dataset_name = st.sidebar.selectbox(
            "Dataset",
            dataset_names,
            help=CASES[
                dataset_names[0]
            ].get(
                "help",
                "No information available."
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

    # ==========================================
    # External CSV
    # ==========================================

    uploaded_file = (
        st.sidebar.file_uploader(
            "Upload CSV",
            type=["csv"]
        )
    )

    if uploaded_file:

        df = pd.read_csv(
            uploaded_file
        )

        cfg = {

            "plugin": None,

            "metrics": [],

            "var_prefix": "var_",

            "default_indicators": []
        }

        return build_dataset(
            df,
            cfg
        )

    return None