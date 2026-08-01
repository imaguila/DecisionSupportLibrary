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
    # Software Release Planning (NRP)
    # =====================================================================

    "MSLite System": {

        # -----------------------------------------------------------------
        # Domain plugin
        # -----------------------------------------------------------------
        # Domain-specific logic used to compute indicators.
        # Implemented in plugins/nrp_plugin.py
        # -----------------------------------------------------------------
        "plugin": "nrp",

        # -----------------------------------------------------------------
        # Pareto front source
        # -----------------------------------------------------------------
        "path_sol": "data/mslitesoluciones.csv",

        # -----------------------------------------------------------------
        # Optimization objectives available in the dataset
        # -----------------------------------------------------------------
        "metrics": [
            "satisfaction",
            "effort",
            "dissatisfaction"
        ],

        # -----------------------------------------------------------------
        # Decision-variable identification
        # -----------------------------------------------------------------
        # Variables will be detected automatically using this prefix:
        #
        # req_1
        # req_2
        # ...
        # req_n
        # -----------------------------------------------------------------
        "var_prefix": "req_",

        "num_x": 16,

        # -----------------------------------------------------------------
        # Columns ignored by the framework
        # -----------------------------------------------------------------
        "exclude_cols": [
            "id",
            "run_id",
            "timestamp"
        ],

        # -----------------------------------------------------------------
        # Default derived indicators suggested by the plugin
        # -----------------------------------------------------------------
        "default_indicators": [
            "scope",
            "productivity",
            "squandering",
            "annoyance",
            "dirtiness"
        ],

        # -----------------------------------------------------------------
        # Dataset reference
        # -----------------------------------------------------------------
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
    # CASE 2
    # Generic Engineering Design
    # =====================================================================

    "Aerospace Wing Design": {

        # -----------------------------------------------------------------
        # Domain plugin
        # -----------------------------------------------------------------
        # Implemented in plugins/aerospace_plugin.py
        # -----------------------------------------------------------------
        "plugin": "aerospace",

        # -----------------------------------------------------------------
        # Pareto front source
        # -----------------------------------------------------------------
        "path_sol": "data/wing_pareto_front.csv",

        # -----------------------------------------------------------------
        # Optimization objectives
        # -----------------------------------------------------------------
        "metrics": [
            "drag",
            "weight"
        ],

        # -----------------------------------------------------------------
        # Decision variables
        # -----------------------------------------------------------------
        # Variables are identified automatically as:
        #
        # var_1
        # var_2
        # ...
        # var_n
        # -----------------------------------------------------------------
        "var_prefix": "var_",

        "num_x": 10,

        # -----------------------------------------------------------------
        # Auxiliary optimizer information
        # -----------------------------------------------------------------
        "exclude_cols": [
            "sim_time",
            "solver_status"
        ],

        # -----------------------------------------------------------------
        # Domain indicators calculated by the aerospace plugin
        # -----------------------------------------------------------------
        "default_indicators": [
            "density",
            "lift_to_drag_ratio",
            "structural_efficiency"
        ],

        # -----------------------------------------------------------------
        # Dataset reference
        # -----------------------------------------------------------------
        "help": (
            "Example, A. et al. (2025). "
            "Multi-objective aerodynamic design optimization "
            "of aircraft wings. Journal of Aircraft, "
            "62(1), 100-115."
        )
    }
}