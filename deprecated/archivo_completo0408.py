
# --- ARCHIVO: __init__.py ---

# plugins/__init__.py

from .nrp_plugin import NRPPlugin
from .aerospace_plugin import AerospacePlugin

PLUGIN_REGISTRY = {
    "nrp": NRPPlugin,
    "aerospace": AerospacePlugin
}

# --- ARCHIVO: aerospace_plugin.py ---

## --------------------------------------------------------------------------------------
## plugins/aerospace_plugin.py


import numpy as np

EPS = 1e-9


class AerospacePlugin:
    """
    Demo aerospace plugin.

    Provides synthetic engineering indicators
    derived from aerodynamic objectives and
    design variables.

    The goal is not physical accuracy but
    demonstrating how a new domain can extend
    the framework through plugins.
    """

    def __init__(self, var_prefix="var_"):

        self.var_prefix = var_prefix

    # --------------------------------------------------
    # Available indicators
    # --------------------------------------------------

    def available_indicators(self):

        return {
            "density",
            "lift_to_drag_ratio",
            "structural_efficiency",
        }

    # --------------------------------------------------
    # Indicator dependencies
    # --------------------------------------------------

    def requirements(self):

        return {

            "density": [
                "weight"
            ],

            "lift_to_drag_ratio": [
                "drag",
                "weight"
            ],

            "structural_efficiency": [
                "drag",
                "weight"
            ]
        }

    # --------------------------------------------------
    # Design variables
    # --------------------------------------------------

    def decision_variables(self, df):

        return [
            c
            for c in df.columns
            if c.startswith(self.var_prefix)
        ]

    # --------------------------------------------------
    # Indicator computation
    # --------------------------------------------------

    def compute_indicators(
        self,
        df,
        selected_indicators
    ):

        result = df.copy()

        vars_cols = self.decision_variables(
            result
        )

        n_vars = max(
            len(vars_cols),
            1
        )

        for indicator in selected_indicators:

            try:

                # ==================================
                # Density
                # ==================================

                if indicator == "density":

                    result[indicator] = (
                        result["weight"]
                        / n_vars
                    )

                # ==================================
                # Lift-to-drag ratio
                # ==================================

                elif (
                    indicator
                    == "lift_to_drag_ratio"
                ):

                    pseudo_lift = (
                        result["weight"]
                        * 0.25
                    )

                    result[indicator] = (
                        pseudo_lift
                        /
                        np.maximum(
                            result["drag"],
                            EPS
                        )
                    )

                # ==================================
                # Structural efficiency
                # ==================================

                elif (
                    indicator
                    == "structural_efficiency"
                ):

                    result[indicator] = (

                        1.0

                        /

                        (
                            (
                                result["drag"]
                                /
                                result["drag"].max()
                            )

                            *

                            (
                                result["weight"]
                                /
                                result["weight"].max()
                            )

                            +

                            EPS
                        )
                    )

            except Exception as exc:

                print(
                    "[AerospacePlugin] "
                    f"Unable to compute "
                    f"{indicator}: {exc}"
                )

        return result

# --- ARCHIVO: base_plugin.py ---

# plugins/base_plugin.py

from abc import ABC, abstractmethod


class DomainPlugin(ABC):

    @abstractmethod
    def available_indicators(self):
        pass

    @abstractmethod
    def compute_indicators(self, df, indicators):
        pass

# --- ARCHIVO: column_classifier.py ---

## --------------------------------------------------------------------------------------
## column_classifier.py

import pandas as pd

class ColumnClassifier:
    """
    Handles dynamic column classification and exclusions based on problem configuration.
    Categorizes dataset attributes into Decision Variables, Base Metrics, and Derived Indicators.
    """
    
    def __init__(self, config: dict):
        self.metrics = set(config.get("metrics", []))
        self.var_prefix = config.get("var_prefix", "x_")
        self.user_excludes = set(config.get("exclude_cols", []))
        
        # Internal system-level columns generated dynamically by the framework
        self.system_excludes = {"highlight", "label", "highlight_label", "score", "cluster", "selected"}

    def get_decision_variables(self, df: pd.DataFrame) -> list:
        """Extracts decision variable columns (X) using the configured prefix."""
        return [col for col in df.columns if col.startswith(self.var_prefix)]

    def get_metrics(self, df: pd.DataFrame) -> list:
        """Extracts base optimization metrics (M) defined in the configuration."""
        return [col for col in df.columns if col in self.metrics]

    def get_derived_indicators(self, df: pd.DataFrame) -> list:
        """
        Extracts derived/enrichment indicators (I).
        Identifies numeric columns that are neither base metrics, decision variables, nor excluded attributes.
        """
        all_excluded = self.system_excludes | self.user_excludes | self.metrics
        
        indicators = []
        for col in df.columns:
            if col in all_excluded or col.startswith(self.var_prefix):
                continue
            # If the column is numeric and passed all exclusion filters, treat it as a derived lens/indicator
            if pd.api.types.is_numeric_dtype(df[col]):
                indicators.append(col)
                
        return indicators

# --- ARCHIVO: config.py ---

## --------------------------------------------------------------------------------------
## config.py
## --------------------------------------------------------------------------------------

"""
Example configurations shipped with the framework.

A configuration describes:

1. How a Pareto front is loaded.
2. Which columns correspond to optimization objectives.
3. How decision variables are identified.
4. Which domain plugin should be used.
5. Which enrichment indicators are available by default.

Users may:
- use an existing configuration,
- define their own configuration,
- or provide an already enriched dataset with no plugin.
"""

CASES = {

    # =====================================================================
    # CASE 1
    # Software Release Planning - CLASSIC Dataset
    # =====================================================================

    "CLASSIC Dataset": {
        "plugin": "nrp",
        "path_sol": "data/bagnallsoluciones.csv",
        "metrics": [
            "satisfaction",
            "effort"
        ],
        "var_prefix": "req_",
        "num_x": 18,
        "exclude_cols": [
            "id",
            "run_id",
            "timestamp"
        ],

        "default_indicators": [
            "scope",
            "productivity",
            "squandering"
        ],

        "help": (
            "Greer, D., & Ruhe, G. (2004). "
            "Software release planning: an evolutionary "
            "and iterative approach. Information and Software "
            "Technology, 46(4), 243-253."
        )
    },

    # =====================================================================
    # CASE 2
    # Software Release Planning - MSLite System
    # =====================================================================

    "MSLite System": {
        "plugin": "nrp",
        "path_sol": "data/mslitesoluciones.csv",
        "metrics": [
            "satisfaction",
            "effort",
            "dissatisfaction"
        ],
        "var_prefix": "req_",
        "num_x": 16,
        "exclude_cols": [
            "id",
            "run_id",
            "timestamp"
        ],

        "default_indicators": [
            "scope",
            "productivity",
            "squandering",
            "annoyance",
            "dirtiness"
        ],

        "help": (
            "Sangwan, R. S., Negahban, A., Nord, R. L., "
            "& Ozkaya, I. (2020). Optimization of software "
            "release planning considering architectural "
            "dependencies, cost, and value. "
            "IEEE Transactions on Software Engineering, "
            "48(4), 1369-1384."
        )
    },

    # =====================================================================
    # CASE 3
    # Replacement Access, Library and ID Card - RALIC
    # =====================================================================

    "Replacement Access, Library and ID Card (RALIC)": {
        "plugin": "nrp",
        "path_sol": "data/ralic.csv",
        "metrics": [
            "satisfaction",
            "effort"
        ],
        "var_prefix": "req_",
        "num_x": 83,
        "exclude_cols": [
            "id",
            "run_id",
            "timestamp"
        ],
        "default_indicators": [
            "scope",
            "productivity",
            "squandering"
        ],
        "help": (
            "Lim, S. L., & Finkelstein, A. (2011). "
            "StakeRare: using social networks and collaborative "
            "filtering for large-scale requirements elicitation. "
            "IEEE Transactions on Software Engineering, "
            "38(3), 707-735."
        )
    },

    # =====================================================================
    # CASE 4
    # Word Processing Software Project
    # =====================================================================

    "Word Processing Software Project": {
        "plugin": "nrp",
        "path_sol": "data/wordprocsoluciones.csv",
        "metrics": [
            "satisfaction",
            "effort",
            "time"
        ],
        "var_prefix": "req_",
        "num_x": 42,
        "exclude_cols": [
            "id",
            "run_id",
            "timestamp"
        ],
        "default_indicators": [
            "scope",
            "productivity",
            "squandering",
            "response",
            "opportunity"
        ],
        "help": (
            "Agarwal, N., Karimpour, R., & Ruhe, G. (2014). "
            "Theme-based product release planning: An analytical "
            "approach. In 2014 47th Hawaii International Conference "
            "on System Sciences, pp. 4739-4748. IEEE."
        )
    },

    # =====================================================================
    # CASE 5
    # Large Dataset - REQ100
    # =====================================================================

    "Large Dataset": {
        "plugin": "nrp",
        "path_sol": "data/req100frente.csv",
        "metrics": [
            "satisfaction",
            "effort"
        ],
        "var_prefix": "req_",
        "num_x": 96,
        "exclude_cols": [
            "id",
            "run_id",
            "timestamp"
        ],
        "default_indicators": [
            "scope",
            "productivity",
            "squandering"
        ],

        "help": (
            "Del Sagrado, J., Del Águila, I. M., "
            "& Orellana, F. J. (2015). Multi-objective "
            "ant colony optimization for requirements selection. "
            "Empirical Software Engineering, 20(3), 577-610."
        )
    },

    # =====================================================================
    # CASE 6
    # ReleasePlanner Dataset - THEME
    # =====================================================================

    "ReleasePlanner™ Dataset": {
        "plugin": "nrp",
        "path_sol": "data/themesoluciones.csv",
        "metrics": [
            "satisfaction",
            "prevalence",
            "cost",
            "dissatisfaction",
            "inestability",
            "effort"
        ],
        "var_prefix": "req_",
        "num_x": 22,
        "exclude_cols": [
            "id",
            "run_id",
            "timestamp"
        ],
        "default_indicators": [
            "scope",
            "productivity",
            "squandering",
            "effectiveness",
            "dirtiness",
            "annoyance",
            "stickiness",
            "fragility",
            "robustness",
            "usage_efficiency"
        ],

        "help": (
            "Karim, M. R., & Ruhe, G. (2014). "
            "Bi-objective genetic search for release planning "
            "in support of themes. In International Symposium "
            "on Search Based Software Engineering, pp. 123-137. "
            "Springer International Publishing."
        )
    },

    # =====================================================================
    # CASE 7
    # Motorola Dataset
    # =====================================================================

    "Motorola Dataset": {
        "plugin": "nrp",
        "path_sol": "data/motorolasoluciones.csv",
        "metrics": [
            "satisfaction",
            "effort"
        ],
        "var_prefix": "req_",
        "num_x": 35,
        "exclude_cols": [
            "id",
            "run_id",
            "timestamp"
        ],
        "default_indicators": [
            "scope",
            "productivity",
            "squandering"
        ],
        "help": (
            "Baker, P., Harman, M., Steinhofel, K., "
            "& Skaliotis, A. (2006). Search based approaches "
            "to component selection and prioritization for the "
            "next release problem. In 2006 22nd IEEE International "
            "Conference on Software Maintenance, pp. 176-185. IEEE."
        )
    },

    # =====================================================================
    # CASE 8
    # Generic Engineering Design - Aerospace Wing Design
    # =====================================================================

    "Aerospace Wing Design": {
        "plugin": "aerospace",
        "path_sol": "data/wing_pareto_front.csv",
        "metrics": [
            "drag",
            "weight"
        ],
        "var_prefix": "var_",
        "num_x": 10,
        "exclude_cols": [
            "sim_time",
            "solver_status"
        ],
        "default_indicators": [
            "density",
            "lift_to_drag_ratio",
            "structural_efficiency"
        ],
        "help": (
            "Example, A. et al. (2025). "
            "Multi-objective aerodynamic design optimization "
            "of aircraft wings. Journal of Aircraft, "
            "62(1), 100-115."
        )
    }
}

# --- ARCHIVO: enrichment.py ---

## --------------------------------------------------------------------------------------
## enrichment.py

import streamlit as st

def render_enrichment( dataset ):

    plugin = dataset["plugin"]

    if plugin is None:
        dataset["selected_indicators"] = []
        return dataset

    selected_metrics = dataset["metrics"]
    available_indicators = []

    requirements = (  plugin.requirements() )

    for indicator, reqs in requirements.items():

        if all(  metric in selected_metrics for metric in reqs ):
            available_indicators.append(  indicator )

    with st.sidebar.expander(
        "⚙️ Data Enrichment",
        expanded=False
    ):
        st.caption( 
            f"ℹ️ Detected {len(available_indicators)} indicators based on active plugin and config."
        )

        selected_indicators = st.multiselect(
            "Avalible candidates for enrichement",
            sorted( available_indicators ),
            default=[
                i
                for i in dataset["config"].get(
                    "default_indicators",
                    []
                )
                if i in available_indicators
            ],
            help=""" 💡Select  to enrich the current
                    decision space.  Only indicators compatible with the selected objectives
                    and supported by the active plugin are available.
                """
        )

    dataset["df"] = plugin.compute_indicators( dataset["df"],  selected_indicators )
    dataset[ "selected_indicators" ] = selected_indicators

    return dataset

# --- ARCHIVO: framing.py ---

## --------------------------------------------------------------------------------------
## framming.py

import streamlit as st
import pandas as pd

def apply_framing(dataset):

    df = dataset["df"].copy()

    dimensions = (  dataset["metrics"] + dataset["selected_indicators"] )

    filtered_df = df.copy()

    with st.sidebar.expander("🎛️ Context Framing",
        expanded=False ):

        # ----------------------------------
        # Dimension filters
        # ----------------------------------

        for metric in dimensions:
            if metric not in df.columns:
                continue
            if not pd.api.types.is_numeric_dtype( df[metric] ):
                continue
            min_v = float( df[metric].min() )
            max_v = float( df[metric].max() )

            if min_v == max_v:
                continue

            selected_range = st.slider(
                metric,  min_value=min_v,  max_value=max_v,
                value=(min_v, max_v),  step=(max_v - min_v) / 1000,
                key=f"framing_{metric}"  )

            if ( abs(selected_range[0] - min_v) < 1e-6 and
                abs(selected_range[1] - max_v) < 1e-6 ):
                continue

            filtered_df = filtered_df[
                (  filtered_df[metric]  >= selected_range[0] )
                &
                (  filtered_df[metric]  <= selected_range[1] )
            ]

        # ----------------------------------
        # Framing summary
        # ----------------------------------

        total_solutions = len(df)

        remaining_solutions = len( filtered_df )

        ratio = (  remaining_solutions
            / max(total_solutions, 1) )

        st.progress(ratio)

        st.markdown(
            f"""
            <div style="text-align:center">
                <div style="font-size:0.9rem;color:gray;">
                    Remaining Solutions
                </div>
                <div style="font-size:1.8rem;font-weight:bold;">
                    {remaining_solutions}/{total_solutions}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(  f"{ratio:.0%} of the decision space is visible." )

    return filtered_df

# --- ARCHIVO: input_panel.py ---

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
    with st.sidebar.expander("🏷️ Input and Preparation", expanded=True):
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
                " → Predefined domain package: " \
                " Dataset + objectives + config + plugin"
            )
        else:
            st.caption(
                "→ Self-contained Pareto-front: " \
                " Standalone dataset + user-defined variable prefix."
            )

        # ==========================================
        # BUILT-IN DATASETS
        # ==========================================

        if mode == "Domain Configuration":
            dataset_names = [
                "-- No Data --"
            ] + list( CASES.keys() )

            dataset_name = st.selectbox(
                "Domain Configuration",
                dataset_names,
                help=(
                    "💡Select a predefined domain package "
                    "containing a Pareto front, objectives, "
                    "indicators in config, and an optional enrichment plugin."
                )
            )

            # --------------------------------------------
            # Nothing selected yet
            # --------------------------------------------
            if dataset_name == "-- No Data --":
                st.info( "Select data to continue." )
                return None

            # --------------------------------------------
            # Load selected configuration
            # --------------------------------------------

            cfg = CASES[ dataset_name ]
            df = pd.read_csv(  cfg["path_sol"] )
            df.reset_index( drop=True, inplace=True )
            df["id"] = range(1, len(df)+1)
            return build_dataset( df,  cfg )

        # ==========================================
        # UPLOAD CSV
        # ==========================================

        uploaded_file = st.file_uploader(
            "Upload CSV",  type=["csv"]
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
            df = pd.read_csv( uploaded_file )
            df.reset_index( drop=True, inplace=True )
            df["id"] = range(1, len(df)+1)
            cfg = {
                "plugin": None,
                "metrics": [],
                "var_prefix":
                    var_prefix,
                "exclude_cols": [],
                "default_indicators":
                    []
            }
            return build_dataset( df, cfg )
    return None

# --- ARCHIVO: lens_diversity.py ---

## --------------------------------------------------------------------------------------
## lens_diversity.py
## --------------------------------------------------------------------------------------

import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans

try:
    from sklearn_extra.cluster import KMedoids
except Exception:
    KMedoids = None

try:
    from sklearn.cluster import HDBSCAN
except Exception:
    HDBSCAN = None


def _valid_numeric_metrics(
    df,
    metrics
):

    return [
        metric
        for metric in metrics
        if (
            metric in df.columns
            and pd.api.types.is_numeric_dtype(
                df[metric]
            )
        )
    ]


def _prepare_matrix(
    df,
    metrics
):

    x = df[
        metrics
    ].copy()

    x = x.fillna(
        x.median(
            numeric_only=True
        )
    )

    scaler = StandardScaler()

    x_scaled = scaler.fit_transform(
        x
    )

    return x_scaled


def _compute_auto_k(
    x_scaled,
    max_k=10
):

    n = len(
        x_scaled
    )

    if n < 3:

        return 1, None

    best_k = 2
    best_score = -1

    upper_k = min(
        max_k,
        n - 1
    )

    for k in range(
        2,
        upper_k + 1
    ):

        try:

            if KMedoids is not None:

                model = KMedoids(
                    n_clusters=k,
                    method="pam",
                    random_state=123
                )

            else:

                model = KMeans(
                    n_clusters=k,
                    random_state=123,
                    n_init=10
                )

            labels = model.fit_predict(
                x_scaled
            )

            if len(set(labels)) > 1:

                score = silhouette_score(
                    x_scaled,
                    labels
                )

                if score > best_score:

                    best_score = score
                    best_k = k

        except Exception:

            pass

    return best_k, best_score


def _fit_kmedoids(
    x_scaled,
    k
):

    if KMedoids is not None:

        model = KMedoids(
            n_clusters=k,
            method="pam",
            random_state=123
        )

        labels = model.fit_predict(
            x_scaled
        )

        method_used = "K-Medoids"

    else:

        model = KMeans(
            n_clusters=k,
            random_state=123,
            n_init=10
        )

        labels = model.fit_predict(
            x_scaled
        )

        method_used = "K-Means fallback"

    return labels, method_used


def _fit_hdbscan(
    x_scaled,
    min_cluster_size
):

    if HDBSCAN is None:

        labels = [
            0
            for _ in range(
                len(x_scaled)
            )
        ]

        method_used = (
            "HDBSCAN unavailable"
        )

        return labels, method_used

    model = HDBSCAN(
        min_cluster_size=min_cluster_size
    )

    labels = model.fit_predict(
        x_scaled
    )

    method_used = "HDBSCAN"

    return labels, method_used


def _add_cluster_labels(
    result,
    labels,
    method_used,
    metrics_used
):

    result = result.copy()

    result[
        "cluster"
    ] = labels

    result[
        "cluster_str"
    ] = result[
        "cluster"
    ].astype(
        str
    )

    result[
        "cluster_str"
    ] = result[
        "cluster_str"
    ].replace(
        "-1",
        "Noise"
    )

    cluster_sizes = (
        result
        .groupby(
            "cluster_str"
        )["id"]
        .transform(
            "size"
        )
    )

    result[
        "group_label"
    ] = (
        "Cluster "
        +
        result["cluster_str"]
        +
        " (n="
        +
        cluster_sizes.astype(
            str
        )
        +
        ")"
    )

    result[
        "diversity_method"
    ] = method_used

    result[
        "diversity_metrics"
    ] = ", ".join(
        metrics_used
    )

    return result


def apply_diversity_lens(
    df,
    dimensions,
    params
):

    result = df.copy()

    method = params.get(
        "method",
        "K-Medoids"
    )

    cluster_metrics = params.get(
        "cluster_metrics",
        dimensions
    )

    cluster_metrics = _valid_numeric_metrics(
        result,
        cluster_metrics
    )

    if len(cluster_metrics) < 2:

        return result

    if len(result) < 2:

        return result

    x_scaled = _prepare_matrix(
        result,
        cluster_metrics
    )

    # ==================================================
    # K-MEDOIDS
    # ==================================================

    if method == "K-Medoids":

        k_mode = params.get(
            "k_mode",
            "Auto"
        )

        if k_mode == "Manual":

            k = params.get(
                "k",
                2
            )

            k = max(
                2,
                min(
                    k,
                    len(result)
                )
            )

            silhouette = None

        else:

            k, silhouette = _compute_auto_k(
                x_scaled
            )

            if k < 2:

                return result

        labels, method_used = _fit_kmedoids(
            x_scaled,
            k
        )

        result = _add_cluster_labels(
            result,
            labels,
            method_used,
            cluster_metrics
        )

        result[
            "diversity_k"
        ] = k

        if silhouette is not None:

            result[
                "diversity_silhouette"
            ] = silhouette


    # ==================================================
    # HDBSCAN
    # ==================================================

    if method == "HDBSCAN":

        n = len(
            result
        )

        size_mode = params.get(
            "cluster_size_mode",
            "Auto"
        )

        if size_mode == "Manual":

            min_cluster_size = params.get(
                "min_cluster_size",
                max(
                    2,
                    int(
                        0.1 * n
                    )
                )
            )

        else:

            granularity = params.get(
                "granularity",
                "Medium (~10%)"
            )

            if granularity == "Small (~5%)":

                min_cluster_size = max(
                    2,
                    int(
                        0.05 * n
                    )
                )

            elif granularity == "Large (~20%)":

                min_cluster_size = max(
                    2,
                    int(
                        0.20 * n
                    )
                )

            else:

                min_cluster_size = max(
                    2,
                    int(
                        0.10 * n
                    )
                )

        labels, method_used = _fit_hdbscan(
            x_scaled,
            min_cluster_size
        )

        result = _add_cluster_labels(
            result,
            labels,
            method_used,
            cluster_metrics
        )
        result[
            "diversity_min_cluster_size"
        ] = min_cluster_size

        exclude_noise = params.get(
            "exclude_noise",
            True
        )

        if exclude_noise:

            result = result[
                result["cluster"] != -1
            ].copy()

        return result

    return result

# --- ARCHIVO: lens_domain.py ---

## --------------------------------------------------------------------------------------
## lens_domain.py
## --------------------------------------------------------------------------------------

import pandas as pd


def apply_domain_lens(
    df,
    maximize,
    minimize,
    top_n
):

    result = df.copy()

    # --------------------------------------------------
    # Sanitize criteria
    # --------------------------------------------------

    maximize = [
        m
        for m in maximize
        if m in result.columns
    ]

    minimize = [
        m
        for m in minimize
        if (
            m in result.columns
            and m not in maximize
        )
    ]

    criteria = (
        maximize
        +
        minimize
    )

    if not criteria:

        return result

    top_n = min(
        top_n,
        len(result)
    )

    ranked_subsets = []

    # ==================================================
    # MAXIMIZATION CRITERIA
    # ==================================================

    for metric in maximize:

        ranked_subsets.append(
            result
            .sort_values(
                metric,
                ascending=False
            )
            .head(top_n)
            [["id"]]
            .assign(
                matched_metric=metric,
                goal="Maximize"
            )
        )

    # ==================================================
    # MINIMIZATION CRITERIA
    # ==================================================

    for metric in minimize:

        ranked_subsets.append(
            result
            .sort_values(
                metric,
                ascending=True
            )
            .head(top_n)
            [["id"]]
            .assign(
                matched_metric=metric,
                goal="Minimize"
            )
        )

    if not ranked_subsets:

        return result

    matches = pd.concat(
        ranked_subsets,
        ignore_index=True
    )

    # --------------------------------------------------
    # Count matches per solution
    # --------------------------------------------------

    counts = (
        matches
        .groupby("id")
        .size()
        .reset_index(
            name="domain_match_count"
        )
    )

    matched_metrics = (
        matches
        .groupby("id")["matched_metric"]
        .apply(
            lambda values: ", ".join(
                sorted(
                    set(values)
                )
            )
        )
        .reset_index(
            name="domain_matched_metrics"
        )
    )

    result = result.merge(
        counts,
        on="id",
        how="left"
    )

    result = result.merge(
        matched_metrics,
        on="id",
        how="left"
    )

    result[
        "domain_match_count"
    ] = result[
        "domain_match_count"
    ].fillna(
        0
    ).astype(
        int
    )

    result[
        "domain_matched_metrics"
    ] = result[
        "domain_matched_metrics"
    ].fillna(
        ""
    )

    # --------------------------------------------------
    # Keep only actual SOI candidates
    # --------------------------------------------------

    result = result[
        result["domain_match_count"] > 0
    ].copy()

    if result.empty:

        return result

    # --------------------------------------------------
    # Labels for visualization
    # --------------------------------------------------

    result[
        "group_base"
    ] = result[
        "domain_match_count"
    ].apply(
        lambda count: f"Matches = {count}"
    )

    group_sizes = (
        result["group_base"]
        .value_counts()
        .to_dict()
    )

    result[
        "group_label"
    ] = result[
        "group_base"
    ].apply(
        lambda group: (
            f"{group} "
            f"(n={group_sizes[group]})"
        )
    )

    # --------------------------------------------------
    # Sort best matches first
    # --------------------------------------------------

    result = result.sort_values(
        [
            "domain_match_count",
            "id"
        ],
        ascending=[
            False,
            True
        ]
    ).copy()

    result[
        "domain_rank"
    ] = range(
        1,
        len(result) + 1
    )

    return result

# --- ARCHIVO: lens_efficiency.py ---

## --------------------------------------------------------------------------------------
## lens_efficiency.py
## --------------------------------------------------------------------------------------

import pandas as pd


EPS = 1e-9


def _normalize_series(
    series
):

    min_v = series.min()
    max_v = series.max()

    if max_v > min_v:

        return (
            series
            -
            min_v
        ) / (
            max_v
            -
            min_v
        )

    return pd.Series(
        0.0,
        index=series.index
    )


def apply_efficiency_lens(
    df,
    method,
    benefit,
    cost,
    top_n
):

    result = df.copy()

    if (
        benefit is None
        or benefit not in result.columns
    ):

        return result

    if cost is None:

        return result

    if isinstance(
        cost,
        str
    ):

        cost_metrics = [
            cost
        ]

    else:

        cost_metrics = [
            c
            for c in cost
            if c in result.columns
        ]

    cost_metrics = [
        c
        for c in cost_metrics
        if c != benefit
    ]

    if len(cost_metrics) == 0:

        return result

    top_n = min(
        top_n,
        len(result)
    )

    # ==================================================
    # BENEFIT / COST RATIO
    # ==================================================

    if method == "Benefit/Cost Ratio":

        cost_metric = cost_metrics[0]

        safe_cost = result[
            cost_metric
        ].replace(
            0,
            EPS
        )

        result[
            "efficiency_score"
        ] = (
            result[benefit]
            /
            safe_cost
        )

    # ==================================================
    # NORMALIZED RATIO
    # ==================================================

    elif method == "Normalized Ratio":

        cost_metric = cost_metrics[0]

        benefit_norm = _normalize_series(
            result[benefit]
        )

        cost_norm = _normalize_series(
            result[cost_metric]
        )

        result[
            "efficiency_score"
        ] = (
            benefit_norm
            /
            (
                cost_norm
                +
                EPS
            )
        )

    # ==================================================
    # DISTANCE TO IDEAL
    # ==================================================

    elif method == "Distance to Ideal":

        cost_metric = cost_metrics[0]

        benefit_norm = _normalize_series(
            result[benefit]
        )

        cost_norm = _normalize_series(
            result[cost_metric]
        )

        distance_to_ideal = (
            (
                1.0
                -
                benefit_norm
            ) ** 2
            +
            (
                cost_norm
            ) ** 2
        ) ** 0.5

        max_distance = (
            2 ** 0.5
        )

        result[
            "efficiency_score"
        ] = (
            1.0
            -
            distance_to_ideal
            /
            max_distance
        )

    # ==================================================
    # COMPOSITE COST RATIO
    # ==================================================

    elif method == "Composite Cost Ratio":

        benefit_norm = _normalize_series(
            result[benefit]
        )

        composite_cost = pd.Series(
            0.0,
            index=result.index
        )

        for cost_metric in cost_metrics:

            composite_cost = (
                composite_cost
                +
                _normalize_series(
                    result[cost_metric]
                )
            )

        composite_cost = (
            composite_cost
            /
            len(cost_metrics)
        )

        result[
            "efficiency_score"
        ] = (
            benefit_norm
            /
            (
                composite_cost
                +
                EPS
            )
        )

        result[
            "efficiency_costs"
        ] = ", ".join(
            cost_metrics
        )

    else:

        return result

    result = result.sort_values(
        "efficiency_score",
        ascending=False
    ).copy()

    result[
        "efficiency_rank"
    ] = range(
        1,
        len(result) + 1
    )

    result[
        "efficiency_method"
    ] = method

    result[
        "efficiency_benefit"
    ] = benefit

    return result.head(
        top_n
    )


# --- ARCHIVO: lens_engine.py ---

## --------------------------------------------------------------------------------------
## lens_engine.py
## --------------------------------------------------------------------------------------

from lenses.lens_preference import (
    apply_preference_lens
)

from lenses.lens_diversity import (
    apply_diversity_lens
)

from lenses.lens_efficiency import (
    apply_efficiency_lens
)

from lenses.lens_indicators import (
    apply_domain_lens
)


def apply_lens(
    df,
    lens_name,
    params,
    dataset
):

    if df is None:

        return df

    if lens_name == "None":

        return df.copy()

    # ==================================================
    # Preference Lens
    # ==================================================

    if lens_name == "Preference":

        return apply_preference_lens(
            df,
            params.get(
                "method",
                "Weighted Sum"
            ),
            params.get(
                "maximize",
                []
            ),
            params.get(
                "minimize",
                []
            ),
            params.get(
                "top_n",
                len(df)
            )
        )

    # ==================================================
    # Diversity Lens
    # ==================================================

    if lens_name == "Diversity":

        dimensions = (
            dataset["metrics"]
            +
            dataset["selected_indicators"]
        )

        return apply_diversity_lens(
            df,
            dimensions,
            params
        )

    # ==================================================
    # Efficiency Lens
    # ==================================================

    if lens_name == "Efficiency":

        return apply_efficiency_lens(
            df,
            params.get(
                "method",
                "Benefit/Cost Ratio"
            ),
            params.get(
                "benefit"
            ),
            params.get(
                "cost"
            ),
            params.get(
                "top_n",
                len(df)
            )
        )

    # ==================================================
    # Indicator Dominance Lens
    # ==================================================

    if lens_name == "Indicator Dominance":

        return apply_domain_lens(
            df,
            params.get(
                "maximize",
                []
            ),
            params.get(
                "minimize",
                []
            ),
            params.get(
                "top_n",
                len(df)
            )
        )

    return df.copy()

# --- ARCHIVO: lens_preference.py ---

## --------------------------------------------------------------------------------------
## lens_preference.py
## --------------------------------------------------------------------------------------

import pandas as pd

def _sanitize_criteria(  df, maximize, minimize ) :
    maximize = [ m for m in maximize if m in df.columns ]
    minimize = [ m for m in minimize if (m in df.columns and m not in maximize) ]
    criteria = ( maximize + minimize )

    return maximize, minimize, criteria

def _minmax_normalize( df, criteria ) :

    norm = pd.DataFrame( index=df.index )
    for metric in criteria:
        min_v = df[metric].min()
        max_v = df[metric].max()
        if max_v > min_v:
            norm[metric] = ( df[metric] - min_v 
            )  / ( max_v  - min_v )
        else:
            norm[metric] = 0.0
    return norm

def _weighted_sum( df, maximize, minimize) :

    criteria =  ( maximize + minimize )
    norm = _minmax_normalize( df, criteria )

    score = pd.Series(  0.0,  index=df.index )
    weight = ( 1.0 / len(criteria) )

    for metric in criteria:
        if metric in maximize:
            score = ( score + weight * norm[metric] )
        else:
            score = ( score +  weight * ( 1.0 - norm[metric] ) )
    return score

def _topsis( df, maximize, minimize ) :

    criteria = ( maximize + minimize)
    norm = df[ criteria ].copy()
    weight = ( 1.0 / len(criteria))
    for metric in criteria:
        denom = (
            norm[metric] ** 2
        ).sum() ** 0.5

        if denom != 0:
            norm[metric] = (  norm[metric] / denom  )
        else:
            norm[metric] = 0.0
        norm[metric] = ( norm[metric] * weight )

    ideal = {}
    anti_ideal = {}

    for metric in criteria:
        if metric in maximize:
            ideal[metric] = ( norm[metric].max())
            anti_ideal[metric] = ( norm[metric].min())
        else:
            ideal[metric] = (  norm[metric].min() )
            anti_ideal[metric] = (  norm[metric].max() )

    scores = []

    for _, row in norm.iterrows():
        d_plus = sum( ( row[metric] - ideal[metric] ) ** 2 
                    for metric in criteria ) ** 0.5
        d_minus = sum( ( row[metric] -  anti_ideal[metric] ) ** 2
                    for metric in criteria ) ** 0.5
        if ( d_plus +  d_minus ) != 0:
            score = ( d_minus / ( d_plus +  d_minus ) )
        else:
            score = 0.0

        scores.append( score )

    return pd.Series( scores, index=df.index )

def _vikor(  df, maximize, minimize, v=0.5) :
    criteria = ( maximize + minimize)

    weight = ( 1.0 / len(criteria) )
    regret = pd.DataFrame( index=df.index )

    for metric in criteria:
        if metric in maximize:
            best = df[metric].max()
            worst = df[metric].min()
        else:
            best = df[metric].min()
            worst = df[metric].max()

        denom = abs( best - worst )

        if denom == 0:
            regret[metric] = 0.0
        else:
            regret[metric] = ( weight *  abs( best - df[metric] ) / denom )

    s_value = regret.sum( axis=1 )
    r_value = regret.max( axis=1 )

    if s_value.max() > s_value.min():
        s_norm = ( s_value - s_value.min()) / ( s_value.max() -  s_value.min() )
    else:
        s_norm = 0.0

    if r_value.max() > r_value.min():
        r_norm = ( r_value -  r_value.min() ) / ( r_value.max() - r_value.min()  )
    else:
        r_norm = 0.0

    q_value = ( v * s_norm + ( 1.0 - v ) * r_norm )

    return ( 1.0 - q_value )

def _reference_point( df, maximize,  minimize):

    criteria = ( maximize +  minimize)
    norm = _minmax_normalize( df, criteria )
    oriented = pd.DataFrame( index=df.index)
    for metric in criteria:
        if metric in maximize:
            oriented[metric] = ( norm[metric])
        else:
            oriented[metric] = ( 1.0 -  norm[metric]  )
    distances = []

    for _, row in oriented.iterrows():

        distance = sum( ( 1.0 - row[metric]) ** 2
            for metric in criteria) ** 0.5

        distances.append( distance )

    distances = pd.Series( distances, index=df.index )

    max_distance = distances.max()

    if max_distance > 0:
        return ( 1.0 - distances /  max_distance )
    return pd.Series( 1.0,  index=df.index )

def apply_preference_lens( df,  method,  maximize, minimize, top_n ):
    result = df.copy()

    maximize, minimize, criteria = _sanitize_criteria( result, maximize,  minimize )

    if not criteria:
        return result

    top_n = min(  top_n,  len(result) )

    if method == "Weighted Sum":
        score = _weighted_sum( result, maximize, minimize )
    elif method == "TOPSIS":
        score = _topsis( result, maximize, minimize )
    elif method == "VIKOR":
        score = _vikor( result, maximize, minimize )
    elif method == "Reference Point":
        score = _reference_point( result, maximize, minimize )
    else:
        return result

    result[ "preference_score"] = score
    result = result.sort_values( "preference_score", ascending=False ).copy()
    result[ "preference_rank" ] = range( 1, len(result) + 1 )
    result[ "preference_method"] = method

    return result.head( top_n )

# --- ARCHIVO: lenses.py ---

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



        # =====================================
        # Lens feedback placeholder
        # =====================================

        lens_feedback = st.empty()

        
        # =====================================
        # Save SOI
        # =====================================

        if "saved_sois" not in st.session_state:

            st.session_state.saved_sois = []

        if active_lens != "None":

            st.markdown("---")

            default_name = (
                f"{active_lens} "
                f"#{len(st.session_state.saved_sois) + 1}"
            )

            if (
                st.session_state.get(
                    "soi_name_lens"
                )
                != active_lens
            ):

                st.session_state[
                    "soi_name"
                ] = default_name

                st.session_state[
                    "soi_name_lens"
                ] = active_lens

            soi_name = st.text_input(
                "Name",
                key="soi_name"
            )

            if st.button(
                "💾 Save Current Set",
                use_container_width=True,
                key="save_current_soi"
            ):

                st.session_state.pending_save_soi = {
                    "name": soi_name,
                    "lens": active_lens,
                    "params": params
                }


    return active_lens, params, lens_feedback
            

# --- ARCHIVO: nrp_plugin.py ---

## --------------------------------------------------------------------------------------
## plugins/nrp_plugin.py

import numpy as np

EPS = 1e-9

class NRPPlugin:
    """
    Minimal NRP plugin.

    Supports only the indicators required by the
    MSLite example configuration shipped with the framework.
    """

    def __init__(self, var_prefix="req_"):
        self.var_prefix = var_prefix

    # --------------------------------------------------
    # Available indicators
    # --------------------------------------------------

    def available_indicators(self):
        return {
            "scope",
            "productivity",
            "squandering",
            "annoyance",
            "dirtiness",
        }

    # --------------------------------------------------
    # Decision variables
    # --------------------------------------------------
    def decision_variables(self, df):
        return [
            c
            for c in df.columns
            if c.startswith(self.var_prefix)
        ]
    
    # --------------------------------------------------
    # Dependencies between indicators 
    # --------------------------------------------------
    def requirements(self):
        return {
            "scope": [],
            "productivity": [
                "satisfaction",
                "effort"
            ],
            "squandering": [
                "effort"
            ],
            "annoyance": [
                "dissatisfaction",
                "satisfaction"
            ],
            "dirtiness": [
                "dissatisfaction",
                "effort"
            ],
        }
    # --------------------------------------------------
    # Indicator computation
    # --------------------------------------------------

    def compute_indicators( self, df, selected_indicators ):
        result = df.copy()
        req_cols = self.decision_variables(result)
        for indicator in selected_indicators:
            try:
                # --------------------------------------
                # Productivity
                # --------------------------------------
                if indicator == "productivity":
                    result[indicator] = ( 
                        result["satisfaction"]
                        / np.maximum(
                            result["effort"],
                            EPS
                        )
                    )
                # --------------------------------------
                # Dirtiness
                # --------------------------------------
                elif indicator == "dirtiness":
                    result[indicator] = np.where(
                        result["dissatisfaction"] == 0,
                        0,
                        result["dissatisfaction"]
                        / np.maximum(
                            result["effort"],
                            EPS
                        )
                    )
                # --------------------------------------
                # Annoyance
                # --------------------------------------
                elif indicator == "annoyance":
                    result[indicator] = np.where(
                        result["dissatisfaction"] == 0,
                        0,
                        result["dissatisfaction"]
                        / np.maximum(
                            result["satisfaction"],
                            EPS
                        )
                    )
                # --------------------------------------
                # Squandering
                # --------------------------------------
                elif indicator == "squandering":
                    effort_max = result["effort"].max()
                    result[indicator] = (
                        effort_max
                        - result["effort"]
                    ) / np.maximum(
                        effort_max,
                        EPS
                    )
                # --------------------------------------
                # Scope
                # --------------------------------------
                elif indicator == "scope":
                    if len(req_cols) > 0:
                        result[indicator] = (
                            result[req_cols]
                            .sum(axis=1)
                            / len(req_cols)
                        )
            except Exception as exc:
                print(
                    f"[NRPPlugin] "
                    f"Unable to compute "
                    f"{indicator}: {exc}"
                )
        return result

# --- ARCHIVO: nrpfull_plugin.py ---

import numpy as np

EPS = 1e-9


class NRPPlugin:

    """
    Next Release Problem (NRP) domain plugin.

    Provides derived indicators commonly used in
    software release planning.
    """

    def __init__(self, var_prefix="req_"):
        self.var_prefix = var_prefix

    # --------------------------------------------------
    # Indicator registry
    # --------------------------------------------------

    def available_indicators(self):

        return {
            "scope",
            "productivity",
            "squandering",
            "annoyance",
            "dirtiness",
            "effectiveness",
            "stickiness",
            "robustness",
            "fragility",
            "response",
            "opportunity",
            "usage_efficiency",
        }

    # --------------------------------------------------
    # Required columns
    # --------------------------------------------------

    def requirements(self):

        return {

            "productivity":
                ["satisfaction", "effort"],

            "effectiveness":
                ["satisfaction", "cost"],

            "dirtiness":
                ["dissatisfaction", "effort"],

            "annoyance":
                ["dissatisfaction", "satisfaction"],

            "stickiness":
                ["prevalence", "effort"],

            "robustness":
                ["satisfaction", "inestability"],

            "fragility":
                ["prevalence", "inestability", "effort"],

            "response":
                ["time", "effort"],

            "opportunity":
                ["satisfaction", "time"],

            "usage_efficiency":
                ["prevalence", "cost"],

            "scope":
                [],

            "squandering":
                ["effort"],
        }

    # --------------------------------------------------
    # Decision variables
    # --------------------------------------------------

    def decision_variables(self, df):

        return [
            c
            for c in df.columns
            if c.startswith(self.var_prefix)
        ]

    # --------------------------------------------------
    # Indicator computation
    # --------------------------------------------------

    def compute_indicators(self, df, indicators):

        result = df.copy()

        req_cols = self.decision_variables(result)

        for indicator in indicators:

            try:

                # ----------------------------------
                # Productivity
                # ----------------------------------

                if indicator == "productivity":

                    result[indicator] = (
                        result["satisfaction"]
                        / np.maximum(result["effort"], EPS)
                    )

                # ----------------------------------
                # Effectiveness
                # ----------------------------------

                elif indicator == "effectiveness":

                    result[indicator] = (
                        result["satisfaction"]
                        / np.maximum(result["cost"], EPS)
                    )

                # ----------------------------------
                # Squandering
                # ----------------------------------

                elif indicator == "squandering":

                    effort_max = result["effort"].max()

                    result[indicator] = (
                        effort_max - result["effort"]
                    ) / np.maximum(effort_max, EPS)

                # ----------------------------------
                # Dirtiness
                # ----------------------------------

                elif indicator == "dirtiness":

                    result[indicator] = np.where(
                        result["dissatisfaction"] == 0,
                        0,
                        result["dissatisfaction"]
                        / np.maximum(result["effort"], EPS)
                    )

                # ----------------------------------
                # Annoyance
                # ----------------------------------

                elif indicator == "annoyance":

                    result[indicator] = np.where(
                        result["dissatisfaction"] == 0,
                        0,
                        result["dissatisfaction"]
                        / np.maximum(
                            result["satisfaction"],
                            EPS
                        )
                    )

                # ----------------------------------
                # Stickiness
                # ----------------------------------

                elif indicator == "stickiness":

                    result[indicator] = (
                        result["prevalence"]
                        / np.maximum(result["effort"], EPS)
                    )

                # ----------------------------------
                # Robustness
                # ----------------------------------

                elif indicator == "robustness":

                    result[indicator] = (
                        result["satisfaction"]
                        / np.maximum(
                            result["inestability"],
                            EPS
                        )
                    )

                # ----------------------------------
                # Fragility
                # ----------------------------------

                elif indicator == "fragility":

                    result[indicator] = (
                        result["prevalence"]
                        * result["inestability"]
                    ) / np.maximum(
                        result["effort"],
                        EPS
                    )

                # ----------------------------------
                # Response
                # ----------------------------------

                elif indicator == "response":

                    result[indicator] = np.where(
                        result["time"] == 0,
                        0,
                        result["time"]
                        / np.maximum(
                            result["effort"],
                            EPS
                        )
                    )

                # ----------------------------------
                # Opportunity
                # ----------------------------------

                elif indicator == "opportunity":

                    result[indicator] = np.where(
                        result["satisfaction"] == 0,
                        0,
                        result["satisfaction"]
                        / np.maximum(
                            result["time"],
                            EPS
                        )
                    )

                # ----------------------------------
                # Usage efficiency
                # ----------------------------------

                elif indicator == "usage_efficiency":

                    result[indicator] = (
                        result["prevalence"]
                        / result["cost"].replace(
                            0,
                            np.nan
                        )
                    ).fillna(0)

                # ----------------------------------
                # Scope
                # ----------------------------------

                elif indicator == "scope":

                    if len(req_cols) > 0:

                        result[indicator] = (
                            result[req_cols].sum(axis=1)
                            / len(req_cols)
                        )

            except Exception as e:

                print(
                    f"[PLUGIN][NRP] "
                    f"Unable to compute {indicator}: {e}"
                )

        return result

# --- ARCHIVO: soi_registry.py ---

## --------------------------------------------------------------------------------------
## soi_registry.py

import streamlit as st

def render_soi_registry():

    if "saved_sois" not in st.session_state:
        st.session_state.saved_sois = []

    with st.expander(
        "📚 Saved SOIs",
        expanded=False
    ):

        if not st.session_state.saved_sois:
            st.info(
                "No saved SOIs."
            )
            return

        if (
            "active_soi_name"
            in st.session_state
        ):
            st.success(
                f"Active SOI: "
                f"{st.session_state.active_soi_name} "
                f"({len(st.session_state.active_soi_ids)} solutions)"
            )

            if st.button(
                "Clear Loaded SOI",
                use_container_width=True,
                key="clear_loaded_soi"
            ):
                if "active_soi_ids" in st.session_state:
                    del st.session_state[
                        "active_soi_ids"
                    ]
                if "active_soi_name" in st.session_state:
                    del st.session_state[
                        "active_soi_name"
                    ]
                st.session_state[
                    "pending_lens_reset"
                ] = True
                st.rerun()
            st.markdown("---")

        for idx, soi in enumerate(
            st.session_state.saved_sois
        ):

            col1, col2, col3 = st.columns(
                [0.62, 0.19, 0.19]
            )

            with col1:
                st.caption(
                    f"{soi['name']} "
                    f"[{len(soi['ids'])}] · "
                    f"{soi.get('lens', 'Unknown')}"
                )

            with col2:
                if st.button(
                    "Load",
                    key=f"load_soi_{idx}",
                    use_container_width=True
                ):
                    st.session_state[
                        "active_soi_ids"
                    ] = soi["ids"]
                    st.session_state[
                        "active_soi_name"
                    ] = soi["name"]
                    st.session_state[
                        "pending_lens_reset"
                    ] = True
                    st.rerun()

            with col3:

                if st.button(
                    "🗑️",
                    key=f"delete_soi_{idx}",
                    use_container_width=True
                ):
                    deleted_name = (
                        st.session_state.saved_sois[idx]["name"]
                    )
                    st.session_state.saved_sois.pop( idx )
                    if (
                        st.session_state.get(
                            "active_soi_name"
                        )
                        == deleted_name
                    ):
                        if "active_soi_ids" in st.session_state:
                            del st.session_state[
                                "active_soi_ids"
                            ]
                        if "active_soi_name" in st.session_state:
                            del st.session_state[
                                "active_soi_name"
                            ]
                    st.rerun()

# --- ARCHIVO: streamlit_app.py ---

## --------------------------------------------------------------------------------------
## streamlit_app.py
## --------------------------------------------------------------------------------------

import streamlit as st

from ui.input_panel import render_input_panel

from core.enrichment import (
    render_enrichment )

from core.framing import (
    apply_framing )

from core.workspace import (
    render_workspace )

from core.workspace_controls import (
    render_workspace_controls )

from lenses.lenses import (
    render_lenses )

from lenses.lens_engine import (
    apply_lens )

st.set_page_config(
    page_title="Decision Space Explorer",
    layout="wide"
)

st.markdown("""
<style>

[data-testid="stExpander"] details summary p {
    font-size: 1.2rem;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)

st.title(
    "Decision Space Explorer"
)

# ==================================================
# INPUT
# ==================================================

dataset = render_input_panel()

if dataset is None:
    st.info( "Select a domain configuration to begin."  )
    st.stop()

# ==================================================
# ENRICHMENT
# ==================================================

dataset = render_enrichment( dataset )

# ==================================================
# WORKSPACE CONTROLS
# ==================================================

dimensions = ( dataset["metrics"] +
    dataset["selected_indicators"]
)

show_ids = render_workspace_controls(
    dimensions
)

# ==================================================
# FRAMING
# ==================================================

framed_df = apply_framing( dataset
)

# ==================================================
# WORKING DATASET
# ==================================================

working_df = framed_df.copy()

if "active_soi_ids" in st.session_state:

    working_df = working_df[
        working_df["id"].isin(
            st.session_state.active_soi_ids
        )
    ].copy()

# ==================================================
# RESET LENS AFTER LOADING SOI
# ==================================================

if st.session_state.get( "pending_lens_reset", False) :
    st.session_state[ "active_lens" ] = "None"
    st.session_state[ "pending_lens_reset" ] = False

# ==================================================
# LENSES / SOI IDENTIFICATION
# ==================================================

active_lens, lens_params, lens_feedback = (  render_lenses( dataset, working_df ) )

lens_df = apply_lens( working_df, active_lens, lens_params, dataset )

# ==================================================
# LENS FEEDBACK
# ==================================================

if lens_feedback is not None:

    with lens_feedback.container():

        if active_lens == "Diversity":

            if "cluster" in lens_df.columns:

                n_clusters = (
                    lens_df["cluster"]
                    .dropna()
                    .astype(int)
                    .loc[
                        lambda s: s != -1
                    ]
                    .nunique()
                )

                st.info(
                    f"Clusters Used: {n_clusters}"
                )

                if "diversity_k" in lens_df.columns:
                    k_value = (
                        lens_df["diversity_k"]
                        .dropna()
                        .iloc[0]
                    )

                if "diversity_silhouette" in lens_df.columns:

                    silhouette_value = (
                        lens_df["diversity_silhouette"]
                        .dropna()
                        .iloc[0]
                    )

                    st.caption(
                        f" Silhouette score: {silhouette_value:.3f}, Cluster Detected: {n_clusters},"
                    )



if lens_df is None:
    st.sidebar.warning(
        "The selected lens returned no dataset. "
        "Reverting to the current working dataset."
    )
    lens_df = working_df.copy()


# ==================================================
# SAVE CURRENT SOI
# ==================================================

if "pending_save_soi" in st.session_state:
    if "saved_sois" not in st.session_state:
        st.session_state.saved_sois = []

    pending = ( st.session_state.pending_save_soi )
    existing_names = [
        soi["name"]
        for soi in st.session_state.saved_sois
    ]

    if pending["name"] in existing_names:
        st.sidebar.warning( "A SOI with this name already exists." )
    else:
        st.session_state.saved_sois.append(
            {
                "name": pending["name"],
                "lens": pending["lens"],
                "params": pending.get(
                    "params",
                    {}
                ),
                "ids": lens_df["id"].tolist()
            }
        )
        st.sidebar.success( f"Saved SOI: {pending['name']}"
        )
    del st.session_state[ "pending_save_soi" ]

# ==================================================
# WORKSPACE
# ==================================================

render_workspace( lens_df, dataset, show_ids )

# --- ARCHIVO: ui_plots.py ---

## --------------------------------------------------------------------------------------
## ui_plot.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def render_scatter_plot(df, x, y, size, color_col, show_ids, key):
    import numpy as np
    import pandas as pd
    import plotly.express as px

    df = df.copy()

    # -----------------------------
    # Hover dinámico
    # -----------------------------
    hover_data = {}
    if "score" in df.columns:
        hover_data["score"] = ':.3f'
    if "score_topsis" in df.columns:
        hover_data["score_topsis"] = ':.3f'
    if "count" in df.columns:
        hover_data["count"] = True
    if "cluster" in df.columns:
        hover_data["cluster"] = True

    # -----------------------------
    # Detectar discreto / continuo
    # -----------------------------
    is_discrete = False

    if color_col and color_col in df.columns:
        if color_col == "group_label":
            is_discrete = True
            df[color_col] = df[color_col].astype(str)

        elif pd.api.types.is_object_dtype(df[color_col]):
            is_discrete = True
            df[color_col] = df[color_col].astype(str)

    # ======================================================
    # ✅ CASO 1: CONTINUO (Weighted, TOPSIS, etc.)
    # ======================================================
    if not is_discrete:

        fig = px.scatter(
            df,
            x=x,
            y=y,
            size=size,
            color=color_col,
            color_continuous_scale=px.colors.sequential.Viridis,
            text="label" if show_ids else None,
            hover_data=hover_data
        )
        fig.update_traces(
            textposition="top right"
        )
        
        # ✅ aplicar opacidad si hay selección
        if "highlight" in df.columns and df["highlight"].any():
            opacity_vals = np.where(df["highlight"], 1.0, 0.25)
            fig.update_traces(marker=dict(opacity=opacity_vals))

        fig.update_layout(
            legend_title_text=color_col if color_col else ""
        )

    # ======================================================
    # ✅ CASO 2: DISCRETO (Clustering, Ranking)
    # ======================================================
    else:




        unique_vals = sorted(df[color_col].dropna().unique().tolist())
        palette = px.colors.qualitative.Plotly
        color_map = {}

        palette_idx = 0
        for v in unique_vals:
            if str(v).startswith("No match"):
                color_map[v] = "#b0b0b0"   # gris para las no coincidencias
            else:
                color_map[v] = palette[palette_idx % len(palette)]
                palette_idx += 1

        fig = px.scatter(
            df,
            x=x,
            y=y,
            size=size,
            color=color_col,
            text="label" if show_ids else None,
            hover_data=hover_data,
            color_discrete_map=color_map
        )

        # ✅ aplicar opacidad también aquí
        if "highlight" in df.columns and df["highlight"].any():
            opacity_vals = np.where(df["highlight"], 1.0, 0.25)
            fig.update_traces(marker=dict(opacity=opacity_vals))

        fig.update_layout(legend_title_text="Groups")

    # -----------------------------
    # Estética
    # -----------------------------
    fig.update_traces(
        textposition="top right",
        textfont=dict(size=10),
        marker=dict(size=10),
        mode='markers+text' if show_ids else 'markers'
    )

    st.plotly_chart(fig, use_container_width=True, key=key)

def plot_radar(selected_df, available_metrics, group_col=None):
    st.markdown("---")

    df_for_compare = selected_df

    
    # -------------------------------
    # Selección de IDs SOLO dentro del grupo elegido
    # -------------------------------
    opciones_id = df_for_compare["id"].unique()
    compare_ids = st.multiselect("👆 Pick solutions to compare", opciones_id)

    if len(compare_ids) < 2:
        st.info("Select at least 2 solutions to compare")
        return


    compare_df = df_for_compare[df_for_compare["id"].isin(compare_ids)].copy()

    tab1, tab2, tab3 = st.tabs([
        "📊 Comparative Profile",
        "👥 Stakeholder Impact",
        "📋 Requirement Composition"#,
       # "🤝 Stakeholder–Requirement Alignment"
    ])

    # ---------- PERFORMANCE ----------
    with tab1:
        st.subheader("Custom Trade-off Comparison")
        
        numeric_cols = [m for m in available_metrics if pd.api.types.is_numeric_dtype(selected_df[m])]
        selected_radar_metrics = st.multiselect(
            "Select metrics (at least 3)", 
            numeric_cols,
            default=numeric_cols[:3] if len(numeric_cols) >= 3 else None,
            key="perf_metrics"
        )

        if len(selected_radar_metrics) >= 3:
            metric_goals = {}
            cols = st.columns(len(selected_radar_metrics))
            
            for idx, m in enumerate(selected_radar_metrics):
                with cols[idx]:
                    goal = st.selectbox(f"Goal {m}", ["Maximize", "Minimize"], key=f"radar_g_{m}")
                    metric_goals[m] = goal

            radar_df = compare_df.copy()
            low, high = 0.1, 0.9

            for m in selected_radar_metrics:
                mi, ma = radar_df[m].min(), radar_df[m].max()
                if ma > mi:
                    norm = (radar_df[m] - mi) / (ma - mi)
                    if metric_goals[m] == "Minimize":
                        norm = 1.0 - norm
                    radar_df[m] = low + (norm * (high - low))
                else:
                    radar_df[m] = 0.5

            fig_perf = go.Figure()
            for _, row in radar_df.iterrows():
                val = row[selected_radar_metrics].tolist()
                val.append(val[0])
                fig_perf.add_trace(go.Scatterpolar(
                    r=val,
                    theta=selected_radar_metrics + [selected_radar_metrics[0]],
                    fill=None,
                    mode='lines+markers',
                    name=f"ID {int(row['id'])}"
                ))

            fig_perf.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True
            )
            st.plotly_chart(fig_perf, use_container_width=True)

        else:
            st.warning("Select at least 3 metrics.")

 # ---------- STAKEHOLDER ----------
    with tab2:
        st.subheader("Coverage per Stakeholder")
        
        stcov_cols = [c for c in selected_df.columns if c.startswith("stcov_")]

        # ----------------------------------
        # ✅ No hay stakeholders
        # ----------------------------------
        if not stcov_cols:
            st.info("No stakeholder coverage columns (stcov_...) found in dataset.")

        else:

            # ----------------------------------
            # ✅ ordenar por relevancia
            # ----------------------------------
            stcov_cols = sorted(
                stcov_cols,
                key=lambda c: selected_df[c].mean(),
                reverse=True
            )

            # ----------------------------------
            # ✅ selección manual (clave)
            # ----------------------------------
            selected_st = st.multiselect(
                "👆 Select stakeholders to display",
                stcov_cols,
                default=stcov_cols[:min(6, len(stcov_cols))]
            )

            # ✅ aplicar selección
            if selected_st:
                stcov_cols = selected_st
            else:
                stcov_cols = []

            st.caption(f"Showing {len(stcov_cols)} stakeholders")

            # ----------------------------------
            # ⚠️ asegurar mínimo
            # ----------------------------------
            if len(stcov_cols) < 3:
                st.warning("Need at least 3 stakeholders to create a radar chart.")
            else:
                cov_df = compare_df.copy()
                low, high = 0.1, 0.9

                for c in stcov_cols:
                    mi, ma = cov_df[c].min(), cov_df[c].max()
                    if ma > mi:
                        norm = (cov_df[c] - mi) / (ma - mi)
                        cov_df[c] = low + (norm * (high - low))
                    else:
                        cov_df[c] = 0.5

                fig_cov = go.Figure()

                for _, row in cov_df.iterrows():
                    val = row[stcov_cols].tolist()
                    val.append(val[0])

                    fig_cov.add_trace(go.Scatterpolar(
                        r=val,
                        theta=stcov_cols + [stcov_cols[0]],
                        fill=None,
                        mode='lines+markers',
                        name=f"ID {int(row['id'])}"
                    ))

                fig_cov.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    showlegend=True
                )

                st.plotly_chart(fig_cov, use_container_width=True)
# ---------- NUEVA PESTAÑA: REQUISITOS ----------
    with tab3:
        st.subheader("Requirements Included in Selected Solutions")
        
        # Detectamos dinámicamente cualquier columna que empiece por "req_"
        req_cols = [c for c in selected_df.columns if c.startswith("req_")]
        
        if not req_cols:
            st.info("No requirement columns (req_...) found in dataset.")
        else:
            # Preparamos los datos: Filas como IDs de solución y columnas como Requisitos
            req_df = compare_df.set_index("id")[req_cols].copy()
            
            # Convertimos el ID a string para el eje Y
            req_df.index = [f"ID {int(i)}" for i in req_df.index]
            
            # MAPA DE COLOR CON CONTRASTE ALTO:
            fig_req = px.imshow(
                req_df,
                labels=dict(x="Requirements", y="Solutions", color="Status"),
                x=req_cols,
                y=req_df.index,
                color_continuous_scale=[[0, "#e0e0e0"], [1, "#00e676"]] # Gris Claro vs Verde Brillante Puro
            )
            
            # Configuramos el diseño del gráfico de forma correcta
            fig_req.update_layout(
                template="plotly_white", # Fondo blanco limpio
                coloraxis_showscale=False, # Ocultamos la barra lateral de colores
                xaxis=dict(
                    tickangle=-45, 
                    showgrid=False, # Quitamos líneas de cuadrícula del fondo
                    tickfont=dict(size=11, color="black") # ¡CORREGIDO AQUÍ! (Era tickfont, no textfont)
                ),
                yaxis=dict(
                    autorange="reversed", 
                    showgrid=False,
                    tickfont=dict(size=11, color="black") # ¡CORREGIDO AQUÍ! (Era tickfont, no textfont)
                ),
                margin=dict(l=50, r=50, t=30, b=50) # Ajustamos márgenes
            )
            
            # Añadimos bordes blancos muy marcados para separar las celdas claramente
            fig_req.update_traces(
                xgap=3, 
                ygap=3,
                hovertemplate="<b>%{y}</b><br>Requirement: %{x}<br>Status: %{z} (1=Included, 0=Excluded)<extra></extra>"
            )
            
            st.plotly_chart(fig_req, use_container_width=True)


# ---------- NUEVA PESTAÑA: ALINEACIÓN STAKEHOLDERS + FILA RESUMEN ----------
#    with tab4:
#        st.subheader("Stakeholder-Requirement Alignment Matrix")
#        st.write("Visualizing which requirements satisfy each stakeholder's specific interests and their final release status.")

        # 1. Identificar columnas
#        req_cols = [c for c in selected_df.columns if c.startswith("req_")]
#        st_cols = [c for c in selected_df.columns if c.startswith("stcov_")]

        # Desplegable para analizar una solución concreta
#        focus_id = st.selectbox("Select Solution to analyze alignment", compare_df["id"].unique(), key="align_sel")
#        row_focus = compare_df[compare_df["id"] == focus_id].iloc[0]

        # Matriz real (requisitos x stakeholders) calculada a partir del
        # dataset del problema (vij) en problem.py::calcular_matriz_solicitud,
        # y guardada en session_state por input_panel.py. Sustituye al
        # antiguo mapeo simulado basado en hash(st_name + req_name).
#        matriz_solicitud = st.session_state.get("matriz_solicitud")

#        if not req_cols or not st_cols:
#            st.info("Required data columns (req_ or stcov_) missing.")
#        elif matriz_solicitud is None:
#            st.info(
#                "No stakeholder-request data available for this dataset "
#                "(e.g. no problem file was loaded, or you are using an "
#                "uploaded CSV). Alignment cannot be computed."
#            )
#        else:

#            alignment_data = []
#            # Generamos las filas de los Stakeholders normales
#            for st_name in st_cols:
#                # "stcov_cv1" -> "cv1", para indexar en matriz_solicitud
#                cliente = st_name.replace("stcov_", "")

#                if cliente not in matriz_solicitud.columns:
                    # Por seguridad, si no encontramos el stakeholder en la
                    # matriz real, lo tratamos como "no solicitado" en vez
                    # de simularlo.
#                    row_values = [0] * len(req_cols)
#                    alignment_data.append(row_values)
#                    continue

#                row_values = []
#                for j, req_name in enumerate(req_cols):
#                    proposed_by_stake = bool(matriz_solicitud.iloc[j][cliente])
#                    is_included = row_focus[req_name] == 1

#                    if proposed_by_stake and is_included:
#                        val = 2  # Solicitado e incluido (Verde brillante)
#                    elif proposed_by_stake and not is_included:
#                        val = 1  # Solicitado pero fuera (Gris medio)
#                    else:
#                        val = 0  # No solicitado (Gris muy claro)
#                    row_values.append(val)
#                alignment_data.append(row_values)

            # --- LA FILA RESUMEN ---
            # Añadimos la fila final que mira directamente si el req está en la solución (1) o no (0)
#            summary_row = []
#            for req_name in req_cols:
#                if row_focus[req_name] == 1:
#                    summary_row.append(3) # Incluido en el release (Verde Oscuro)
#                else:
#                    summary_row.append(1) # Fuera del release (Gris Medio)
#            alignment_data.append(summary_row)

            # Creamos la lista de nombres para el eje Y incluyendo nuestro resumen
#            y_labels = [s.replace("stcov_", "Stakeholder ") for s in st_cols] + ["📦 RELEASE STATUS"]

            # Crear DataFrame para el Heatmap
#            align_df = pd.DataFrame(alignment_data, index=y_labels, columns=req_cols)

            # 2. Construir el Heatmap con Escala de 4 colores discretos
#            fig_align = px.imshow(
#                align_df,
#                labels=dict(x="Requirements", y="Alignment Status", color="Status"),
#                x=req_cols,
#                y=y_labels,
                # Definimos los cortes exactos de color para 0, 1, 2 y 3
#                color_continuous_scale=[
#                    [0.0, "#f8f9fa"],   # 0: Sin interés (Blanco/Gris suave)
#                    [0.33, "#adb5bd"],  # 1: Fuera del Release / Deuda (Gris medio)
#                    [0.66, "#00e676"],  # 2: Solicitado e Incluido (Verde brillante)
#                    [1.0, "#00695c"]    # 3: Fila Resumen - ¡En el Release! (Verde Oscuro Azulado)
#                ]
#            )

            # Diseño limpio del gráfico
#            fig_align.update_layout(
#               template="plotly_white",
#                coloraxis_showscale=False, # Ocultamos barra de escala continua
#                xaxis=dict(tickangle=-45, tickfont=dict(size=11, color="black")),
#                yaxis=dict(tickfont=dict(size=11, color="black")),
#                height=450
#            )

            # Espaciado de celdas y caja de información al pasar el ratón (Hover)
#            fig_align.update_traces(
#                xgap=3, ygap=3,
#                hovertemplate="<b>%{y}</b><br>Requirement: %{x}<extra></extra>"
#            )

#            st.plotly_chart(fig_align, use_container_width=True)
            
            # Leyenda explicativa interactiva en columnas abajo del gráfico
#            c1, c2, c3= st.columns(3)
#            c1.markdown("⚪ **Not requested**")
#            c2.markdown("🔘 **Requested (Not included) / Excluded from the Release**")
#            c3.markdown("🟢 **Requested and Included (Stakeholder)**")
          #  c4.markdown("🌲 **Included in the Final Release (Summary Row)**")

# --------------------------------------------

# --- ARCHIVO: visualization.py ---

## --------------------------------------------------------------------------------------
## visualization.py

import plotly.express as px
import streamlit as st


def render_scatter(
    df,
    x,
    y,
    size=None,
    color=None,
    show_ids=False,
    key=None
):

    text_column = None

    if show_ids:

        if "id" in df.columns:

            text_column = "id"

        elif "ID" in df.columns:

            text_column = "ID"

    # --------------------------------------------------
    # Automatic lens-aware color
    # --------------------------------------------------
    # Priority:
    # 1. Clustering / indicator groups
    # 2. Preference scores
    # 3. Efficiency scores
    # 4. User-selected color

    plot_color = color

    if "group_label" in df.columns:

        plot_color = "group_label"

    elif "cluster_str" in df.columns:

        plot_color = "cluster_str"

    elif "preference_score" in df.columns:

        plot_color = "preference_score"

    elif "efficiency_score" in df.columns:

        plot_color = "efficiency_score"

    elif "domain_match_count" in df.columns:

        plot_color = "domain_match_count"

    # --------------------------------------------------
    # Clean hover data
    # --------------------------------------------------

    hover_cols = [

        c

        for c in df.columns

        if not (
            c.startswith("req_")
            or c.startswith("var_")
            or c.startswith("x_")
        )

    ]

    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=plot_color,
        text=text_column,
        hover_data=hover_cols
    )

    fig.update_traces(
        textposition="top center"
    )

    fig.update_layout(
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key
    )


def render_coordinated_maps( df, x, y, z, key_prefix, show_ids=False) :
    col1, col2 = st.columns(2)
    with col1:
        st.caption( f"{x} vs {y}" )
        render_scatter( df, x=x, y=y, show_ids=show_ids, key=f"{key_prefix}_left" )
    with col2:
        st.caption( f"{x} vs {z}" )
        render_scatter( df, x=x, y=z, show_ids=show_ids, key=f"{key_prefix}_right" )

def render_distribution( df, metric, mode="Violin", key=None ) :
    if mode == "Violin":
        fig = px.violin( df, y=metric, box=True, points="all" )
    else:
        fig = px.box( df, y=metric, points="all" )

    fig.update_layout( title=f"Distribution of {metric}",
        height=550, showlegend=False, template="plotly_white"
    )
    st.plotly_chart( fig, use_container_width=True, key=key )

# --- ARCHIVO: workspace.py ---

## --------------------------------------------------------------------------------------
## workspace.py
## --------------------------------------------------------------------------------------

import streamlit as st

from core.workspace_summary import (
        render_summary )
from core.workspace_maps import (
    render_maps )
from core.workspace_dataset import (
    render_dataset_preview )
from soi.soi_registry import (
    render_soi_registry )

def render_workspace( df, dataset,  show_ids) :

    if df is None:
        st.error( "No dataset is available for the workspace." )
        return

    dimensions = ( dataset["metrics"] +
        dataset["selected_indicators"] )

    render_summary( df, dataset )

    if len(dimensions) < 2:
        st.warning(
            "At least two dimensions are required "
            "to render decision-space maps."
        )

        render_soi_registry()
        render_dataset_preview( df, dataset )

        return

    render_maps( df, dataset, dimensions, show_ids )
    render_soi_registry()
    render_dataset_preview( df, dataset )

# --- ARCHIVO: workspace_controls.py ---

## --------------------------------------------------------------------------------------
## workspace_control.py

import streamlit as st

def render_workspace_controls(
    dimensions
):

    with st.sidebar.expander(
        "🗺️ Visual Workspace",
        expanded=False
    ):

        col1, col2 = st.columns(
            [0.50, 0.50]
        )
        if "maps" not in st.session_state:
            st.session_state.maps = []

        with col1:
            if st.button(
                "🔄 Reset Maps",
                use_container_width=True
            ):
                st.session_state.maps = [
                    {
                        "x": dimensions[0],  "y": dimensions[1],
                        "z": None,  "color": None
                    }
                ]
                st.rerun()
        with col2:
            if st.button(
                "New Map",
                use_container_width=True
            ):
                st.session_state.maps.append(
                    {
                        "x": dimensions[0],  "y": dimensions[1],
                        "z": None,  "color": None
                    }
                )

                st.rerun()

        show_ids = st.checkbox(  "Show solution IDs", value=False )

        st.caption(
            f"Active maps: "
            f"{len(st.session_state.maps)}"
        )

    return show_ids

# --- ARCHIVO: workspace_dataset.py ---

## --------------------------------------------------------------------------------------
## workspace_dataset.py

import streamlit as st

def render_dataset_preview(   df,  dataset ):

    with st.expander(
        f"📋 Current Dataset "
        f"(prefix: "
        f"{dataset['config'].get('var_prefix')})",
        expanded=False
    ):
        var_prefix = dataset["config"].get(
            "var_prefix",
            "x_"
        )
        objective_cols = dataset["metrics"]
        indicator_cols = dataset["selected_indicators"]
        decision_cols = [
            c
            for c in df.columns
            if c.startswith(
                var_prefix
            )
        ]
        other_cols = [
            c
            for c in df.columns
            if (
                c not in objective_cols
                and c not in indicator_cols
                and c not in decision_cols
                and c != "id"
            )
        ]

        ordered_cols = (  ["id"] + objective_cols +  indicator_cols
            + other_cols + decision_cols )

        ordered_cols = [
            c
            for c in ordered_cols
            if c in df.columns
        ]

        st.dataframe(  df[ordered_cols],  use_container_width=True,
            height=500,  hide_index=True )


# --- ARCHIVO: workspace_maps.py ---

## --------------------------------------------------------------------------------------
## workspace_maps.py

import streamlit as st

from ui.visualization import (
    render_scatter,
    render_coordinated_maps,
    render_distribution  )

def render_maps(
    df,
    dataset,
    dimensions,
    show_ids
):
    if len(st.session_state.maps) == 0:

        st.info(
            "No decision maps have been created yet. "
            "Use 'New Map' in the Visual Workspace panel."
        )

        return
    for idx in range(
        len(st.session_state.maps)
    ):
        current_map = (
            st.session_state.maps[idx]
        )

        with st.expander(
            f"🗺️ Decision-Space Map {idx + 1}",
            expanded=(idx == 0)
        ):

            if len(dimensions) < 2:

                st.warning(
                    "At least two dimensions are required."
                )

                continue

            # =====================================
            # VISUALIZATION MODE
            # =====================================

            map_mode = st.radio(
                "Visualization Mode",
                [
                    "🗺️ Scatter",
                    "🫧 Bubble",
                    "📈 Distribution"
                ],
                horizontal=True,
                key=f"map_mode_{idx}"
            )

            x = current_map.get("x")
            y = current_map.get("y")
            z = current_map.get("z")
            color = current_map.get("color")

            # =====================================
            # SCATTER / BUBBLE
            # =====================================
            
            if map_mode in [
                "🗺️ Scatter",
                "🫧 Bubble"
            ]:

                if map_mode == "🗺️ Scatter":
                    c1, c2, c3 = st.columns(3)
                else:
                    c1, c2, c3, c4 = st.columns(4)

                with c1:

                    current_x = (
                        current_map["x"]
                        if current_map["x"] in dimensions
                        else dimensions[0]
                    )

                    x = st.selectbox(
                        "X Axis",
                        dimensions,
                        index=dimensions.index(
                            current_x
                        ),
                        key=f"x_{idx}"
                    )

                with c2:

                    y_options = [

                        d

                        for d in dimensions

                        if d != x

                    ]

                    current_y = (
                        current_map["y"]
                        if current_map["y"] in y_options
                        else y_options[0]
                    )

                    y = st.selectbox(
                        "Y Axis",
                        y_options,
                        index=y_options.index(
                            current_y
                        ),
                        key=f"y_{idx}"
                    )

                with c3:

                    z_options = [None] + [

                        d

                        for d in dimensions

                        if d not in [x, y]

                    ]

                    current_z = (
                        current_map["z"]
                        if current_map["z"] in z_options
                        else None
                    )

                    z = st.selectbox(
                        "Third Dimension",
                        z_options,
                        index=z_options.index(
                            current_z
                        ),
                        key=f"z_{idx}"
                    )

                if map_mode == "🫧 Bubble":

                    with c4:

                        color_options = (
                            [None]
                            + dimensions
                        )

                        current_color = (
                            current_map["color"]
                            if current_map["color"]
                            in color_options
                            else None
                        )

                        color = st.selectbox(
                            "Color",
                            color_options,
                            index=color_options.index(
                                current_color
                            ),
                            key=f"color_{idx}"
                        )

                else:

                    color = None

                # ----------------------------------
                # Render Scatter
                # ----------------------------------

                if map_mode == "🗺️ Scatter":

                    if z is None:

                        render_scatter(
                            df,
                            x=x,
                            y=y,
                            color=None,
                            show_ids=show_ids,
                            key=f"single_{idx}"
                        )

                    else:

                        render_coordinated_maps(
                            df,
                            x=x,
                            y=y,
                            z=z,
                            key_prefix=f"coord_{idx}",
                            show_ids=show_ids
                        )

                # ----------------------------------
                # Render Bubble
                # ----------------------------------

                else:

                    render_scatter(
                        df,
                        x=x,
                        y=y,
                        size=(
                            z
                            if z is not None
                            else None
                        ),
                        color=color,
                        show_ids=show_ids,
                        key=f"bubble_{idx}"
                    )

            # =====================================
            # DISTRIBUTION
            # =====================================

            else:

                x = current_map["x"]
                y = current_map["y"]
                z = None
                color = None

                view_type = st.radio(
                    "View",
                    [
                        "Violin",
                        "Box"
                    ],
                    horizontal=True,
                    key=f"dist_mode_{idx}"
                )

                distribution_metric = st.selectbox(
                    "Dimension",
                    dimensions,
                    key=f"distribution_{idx}"
                )

                render_distribution(
                    df,
                    metric=distribution_metric,
                    mode=view_type,
                    key=f"distribution_plot_{idx}"
                )

            # =====================================
            # SAVE MAP STATE
            # =====================================

            st.session_state.maps[idx] = {

                "x": x,
                "y": y,
                "z": z,
                "color": color

            }

# --- ARCHIVO: workspace_summary.py ---

import streamlit as st

def render_summary( df, dataset ):

    if df is None:
        st.error(
            "Dataset summary cannot be rendered "
            "because the current dataframe is empty."
        )
        return

    with st.expander(  "📊 Dataset Summary", expanded=False ):

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric( "Solutions", len(df) )
        with c2:
            st.metric( "Attributes",  len(df.columns) )
        with c3:
            st.metric( "Decision Variables", len( dataset[ "decision_variables" ] ) )

        st.caption(
            f"Decision-variable prefix: "
            f"{dataset['config'].get('var_prefix')}"
        )

        st.download_button(
            label="⬇️ Export Current Subset",
            data=df.to_csv(  index=False ),
            file_name="current_subset.csv",
            mime="text/csv",
            use_container_width=True
        )
