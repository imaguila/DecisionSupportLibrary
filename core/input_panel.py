## --------------------------------------------------------------------------------------
## input_panel.py
## --------------------------------------------------------------------------------------


import streamlit as st
import pandas as pd

from config import CASES
from plugins import PLUGIN_REGISTRY


def detect_decision_variables(
    df,
    prefix
):

    return [
        col
        for col in df.columns
        if col.startswith(
            prefix
        )
    ]


def infer_numeric_metrics(
    df,
    cfg
):

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

    system_cols = {
        "id",
        "ID",
        "cluster",
        "cluster_str",
        "group_label",
        "group_base",
        "label",
        "highlight",
        "highlight_label",
        "score",
        "preference_score",
        "preference_rank",
        "efficiency_score",
        "efficiency_rank",
        "domain_match_count",
        "domain_rank",
        "selected"
    }

    metrics = []

    for col in df.columns:

        if col.startswith(
            var_prefix
        ):
            continue

        if col in excluded:
            continue

        if col in system_cols:
            continue

        if pd.api.types.is_numeric_dtype(
            df[col]
        ):
            metrics.append(
                col
            )

    return metrics


def build_plugin(
    cfg
):

    plugin = None

    plugin_name = cfg.get(
        "plugin"
    )

    if plugin_name:

        plugin_class = PLUGIN_REGISTRY.get(
            plugin_name
        )

        if plugin_class is not None:

            plugin = plugin_class(
                var_prefix=cfg.get(
                    "var_prefix",
                    "x_"
                )
            )

    return plugin


def build_dataset(
    df,
    cfg
):

    plugin = build_plugin(
        cfg
    )

    all_metrics = cfg.get(
        "metrics",
        []
    )

    if not all_metrics:

        all_metrics = infer_numeric_metrics(
            df,
            cfg
        )

    selected_metrics = st.multiselect(
        "Optimization Objectives",
        all_metrics,
        default=all_metrics,
        help=(
            "Select the objective columns that define "
            "the base decision space."
        )
    )

    decision_variables = detect_decision_variables(
        df,
        cfg.get(
            "var_prefix",
            "x_"
        )
    )

    return {
        "df": df,
        "config": cfg,
        "plugin": plugin,
        "metrics": selected_metrics,
        "selected_indicators": [],
        "decision_variables": decision_variables
    }


def load_builtin_dataset(
    cfg
):

    df = pd.read_csv(
        cfg["path_sol"]
    )

    df = df.reset_index(
        drop=True
    )

    df["id"] = range(
        1,
        len(df) + 1
    )

    return df


def load_uploaded_dataset(
    uploaded_file
):

    df = pd.read_csv(
        uploaded_file
    )

    df = df.reset_index(
        drop=True
    )

    df["id"] = range(
        1,
        len(df) + 1
    )

    return df


def render_input_panel():

    with st.sidebar.expander(
        "🏷️ Input and Preparation",
        expanded=True
    ):

        mode = st.radio(
            "Data Source",
            [
                "Domain Configuration",
                "Upload Enriched CSV"
            ],
            horizontal=True,
            help="Choose how the decision space is loaded."
        )

        if mode == "Domain Configuration":

            st.caption(
                "Predefined package: dataset, objectives, "
                "configuration and optional plugin."
            )

            dataset_names = [
                "-- No Data --"
            ] + list(
                CASES.keys()
            )

            dataset_name = st.selectbox(
                "Domain Configuration",
                dataset_names
            )

            if dataset_name == "-- No Data --":

                st.info(
                    "Select data to continue."
                )

                return None

            cfg = CASES[
                dataset_name
            ]

            try:

                df = load_builtin_dataset(
                    cfg
                )

            except Exception as exc:

                st.error(
                    f"Unable to load dataset: {cfg.get('path_sol')}"
                )

                st.exception(
                    exc
                )

                return None

            if cfg.get(
                "help"
            ):

                st.caption(
                    cfg["help"]
                )

            return build_dataset(
                df,
                cfg
            )

        st.caption(
            "Self-contained Pareto front: standalone CSV "
            "with user-defined variable prefix."
        )

        uploaded_file = st.file_uploader(
            "Upload CSV",
            type=[
                "csv"
            ]
        )

        if uploaded_file is None:

            return None

        var_prefix = st.text_input(
            "Decision-variable prefix",
            value="var_",
            help=(
                "Prefix used to identify decision variables, "
                "for example req_, var_, x_, feature_ or design_."
            )
        )

        try:

            df = load_uploaded_dataset(
                uploaded_file
            )

        except Exception as exc:

            st.error(
                "Unable to load uploaded CSV."
            )

            st.exception(
                exc
            )

            return None

        cfg = {
            "plugin": None,
            "metrics": [],
            "var_prefix": var_prefix,
            "exclude_cols": [],
            "default_indicators": [],
            "help": "Uploaded enriched CSV."
        }

        return build_dataset(
            df,
            cfg
        )