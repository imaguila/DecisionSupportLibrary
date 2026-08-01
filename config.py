CASES = {
    # -------------------------------------------------------------------------
    # CASE 1: Software Domain (Next Release Problem - NRP)
    # -------------------------------------------------------------------------
    "MSLite System": {
        "path_sol": "data/mslitesoluciones.csv",
        "metrics": ["satisfaction", "effort", "dissatisfaction"],
        "var_prefix": "req_",  # Prefix identifying decision variables
        "num_x": 16,
        "exclude_cols": ["id", "run_id", "timestamp"],  # Columns to ignore during analysis
        "default_indicators": [
            "scope",
            "productivity",
            "squandering",
            "annoyance",
            "dirtiness",
        ],
        "help": "Sangwan, R. S., Negahban, A., Nord, R. L., & Ozkaya, I. (2020). Optimization of software release planning considering architectural dependencies, cost, and value. IEEE Transactions on Software Engineering, 48(4), 1369-1384.",
    },

    # -------------------------------------------------------------------------
    # CASE 2: Generic Engineering Domain (Aerospace Wing Design)
    # -------------------------------------------------------------------------
    "Aerospace Wing Design": {
        "path_sol": "data/wing_pareto_front.csv",
        "metrics": ["drag", "weight"],  # Base optimization metrics
        "var_prefix": "var_",  # Decision variables prefix (var_0, var_1...)
        "num_x": 10,  # 10 continuous/discrete design parameters
        "exclude_cols": ["sim_time", "solver_status"],  # Auxiliary metadata from optimizer
        "default_indicators": [
            "density",
            "lift_to_drag_ratio",
            "structural_efficiency",
        ],
        "help": "Example, A. et al. (2025). Multi-objective aerodynamic design optimization of aircraft wings. Journal of Aircraft, 62(1), 100-115.",
    },
}