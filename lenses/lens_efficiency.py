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
