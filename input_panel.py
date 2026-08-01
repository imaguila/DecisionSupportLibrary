import streamlit as st
import pandas as pd

from config import CASES

from plugins import PLUGIN_REGISTRY

from enrichment import (
    detect_available_indicators,
    apply_enrichment
)


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

    # ----------------------------------
    # ENRICHMENT SIDEBAR
    # ----------------------------------

    selected_indicators = []

    if plugin:

        available = (
            detect_available_indicators(
                plugin
            )
        )

        st.sidebar.markdown(
            "## Enrichment"
        )

        selected_indicators = (
            st.sidebar.multiselect(
                "Available Indicators",
                available,
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

    # ----------------------------------

    dataset = {

        "df": df,

        "config": cfg,

        "plugin": plugin,

        "metrics": cfg.get(
            "metrics",
            []
        ),

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


def render_input_panel():

    st.sidebar.header(
        "Input Data"
    )

    mode = st.sidebar.radio(
        "Input Mode",
        [
            "Example Dataset",
            "Upload Enriched CSV"
        ]
    )

    # ==================================
    # EXAMPLES
    # ==================================

    if mode == "Example Dataset":

        case_name = (
            st.sidebar.selectbox(
                "Dataset",
                list(CASES.keys())
            )
        )

        cfg = CASES[case_name]

        with st.sidebar.expander(
            "ℹ Dataset Information",
            expanded=False
        ):
            st.write(
                cfg["help"]
            )

        if st.sidebar.button(
            "Load Dataset"
        ):

            df = pd.read_csv(
                cfg["path_sol"]
            )

            return build_dataset(
                df,
                cfg
            )

    # ==================================
    # ENRICHED CSV
    # ==================================

    else:

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