## --------------------------------------------------------------------------------------
## input_panel.py

import streamlit as st
import pandas as pd

from config import CASES
from plugins import PLUGIN_REGISTRY

# =====================================================
# HELPERS
# =====================================================

def detect_decision_variables( df, prefix ):
    return [ c for c in df.columns if c.startswith(prefix) ]

def build_dataset( df, cfg ):
    plugin = None
    plugin_name = cfg.get( "plugin")

    if plugin_name:
        plugin_class = (
            PLUGIN_REGISTRY.get( plugin_name )
        )
        if plugin_class:
            plugin = plugin_class(  var_prefix=cfg.get( "var_prefix", "x_" ) )

    # =================================================
    # OBJECTIVES
    # =================================================

    all_metrics = cfg.get( "metrics", [] )

    if not all_metrics:
        var_prefix = cfg.get( "var_prefix", "x_" )
        excluded = set( cfg.get( "exclude_cols", [] ))
        all_metrics = []
        for col in df.columns:
            if col.startswith( var_prefix ):
                continue
            if col in excluded:
                continue
            if col in [ "id", "highlight",
                "label", "cluster",  "score"]:
                continue
            if pd.api.types.is_numeric_dtype( df[col] ):
                all_metrics.append(col)

    selected_metrics = st.multiselect( "Optimization Objectives",
        all_metrics, default=all_metrics )

    dataset = { "df": df, "config": cfg, "plugin": plugin,
        "metrics": selected_metrics, "selected_indicators":
        [], "decision_variables":
            detect_decision_variables(
                df, cfg.get( "var_prefix", "x_")
            )
    }
    return dataset


# =====================================================
# MAIN PANEL
# =====================================================

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
            help="💡Choose how the decision space is loaded."
        )

        if mode == "Domain Configuration":

            st.caption(
                " → Predefined domain package: "
                " Dataset + objectives + config + plugin"
            )

        else:

            st.caption(
                "→ Self-contained Pareto-front: "
                " Standalone dataset + user-defined variable prefix."
            )

        # ==========================================
        # BUILT-IN DATASETS
        # ==========================================

        if mode == "Domain Configuration":

            dataset_names = [
                "-- No Data --"
            ] + list(
                CASES.keys()
            )

            col_dataset, col_help = st.columns(
                [
                    0.85,
                    0.15
                ],
                vertical_alignment="bottom"
            )

            with col_dataset:

                dataset_name = st.selectbox(
                    "Domain Configuration",
                    dataset_names,
                    key="input_domain_configuration"
                )

            if dataset_name == "-- No Data --":

                dataset_help = (
                    "No domain configuration selected yet.\n\n"
                    "Choose a predefined case to load its dataset, objectives, "
                    "decision-variable prefix, and optional plugin."
                )

            else:

                dataset_help = CASES[
                    dataset_name
                ].get(
                    "help",
                    (
                        "No additional description is available for this "
                        "domain configuration."
                    )
                )

            with col_help:

                render_help_icon(
                    dataset_help,
                    key="help_domain_configuration"
                )

            # --------------------------------------------
            # Nothing selected yet
            # --------------------------------------------

            if dataset_name == "-- No Data --":

                st.info(
                    "Select data to continue."
                )

                return None

            # --------------------------------------------
            # Load selected configuration
            # --------------------------------------------

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

            df[
                "id"
            ] = range(
                1,
                len(df) + 1
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
            type=[
                "csv"
            ]
        )

        if uploaded_file:

            var_prefix = st.text_input(
                "Decision-variable prefix",
                value="var_",
                help=(
                    "Prefix used to identify "
                    "decision variables "
                    "(e.g. req_, var_, x_, "
                    "feature_, design_)."
                )
            )

            df = pd.read_csv(
                uploaded_file
            )

            df.reset_index(
                drop=True,
                inplace=True
            )

            df[
                "id"
            ] = range(
                1,
                len(df) + 1
            )

            cfg = {
                "plugin": None,
                "metrics": [],
                "var_prefix": var_prefix,
                "exclude_cols": [],
                "default_indicators": []
            }

            return build_dataset(
                df,
                cfg
            )

    return None