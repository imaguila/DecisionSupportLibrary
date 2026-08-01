import streamlit as st
import pandas as pd

from config import CASES
from plugins import PLUGIN_REGISTRY


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
                var_prefix=cfg["var_prefix"]
            )

            indicators = cfg.get(
                "default_indicators",
                []
            )

            if indicators:

                df = plugin.compute_indicators(
                    df,
                    indicators
                )

    dataset = {

        "df": df,

        "config": cfg,

        "plugin": plugin,

        "metrics": cfg.get(
            "metrics",
            []
        ),

        "decision_variables":
            detect_decision_variables(
                df,
                cfg["var_prefix"]
            )
    }

    return dataset


def render_input_panel():

    st.sidebar.header("Input Data")

    mode = st.sidebar.radio(
        "Input Mode",
        [
            "Example Dataset",
            "Upload Enriched CSV"
        ]
    )

    # ------------------------------------------------
    # Example Dataset
    # ------------------------------------------------

    if mode == "Example Dataset":

        case_name = st.sidebar.selectbox(
            "Dataset",
            list(CASES.keys())
        )

        cfg = CASES[case_name]

        st.sidebar.info(cfg["help"])

        if st.sidebar.button("Load Dataset"):

            df = pd.read_csv(
                cfg["path_sol"]
            )

            return build_dataset(
                df,
                cfg
            )

    # ------------------------------------------------
    # Upload CSV
    # ------------------------------------------------

    else:

        uploaded_file = st.sidebar.file_uploader(
            "Upload enriched CSV",
            type=["csv"]
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