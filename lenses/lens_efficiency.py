## --------------------------------------------------------------------------------------
## lens_efficiency.py
## --------------------------------------------------------------------------------------

import pandas as pd

EPS = 1e-9

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
        or cost is None
        or benefit not in result.columns
        or cost not in result.columns
        or benefit == cost
    ):

        return result

    top_n = min(
        top_n,
        len(result)
    )

    # ==================================================
    # RAW BENEFIT / COST RATIO
    # ==================================================

    if method == "Benefit/Cost Ratio":

        safe_cost = result[
            cost
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

        benefit_min = result[
            benefit
        ].min()

        benefit_max = result[
            benefit
        ].max()

        cost_min = result[
            cost
        ].min()

        cost_max = result[
            cost
        ].max()

        if benefit_max > benefit_min:

            benefit_norm = (
                result[benefit]
                -
                benefit_min
            ) / (
                benefit_max
                -
                benefit_min
            )

        else:

            benefit_norm = pd.Series(
                0.0,
                index=result.index
            )

        if cost_max > cost_min:

            cost_norm = (
                result[cost]
                -
                cost_min
            ) / (
                cost_max
                -
                cost_min
            )

        else:

            cost_norm = pd.Series(
                0.0,
                index=result.index
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

        benefit_min = result[
            benefit
        ].min()

        benefit_max = result[
            benefit
        ].max()

        cost_min = result[
            cost
        ].min()

        cost_max = result[
            cost
        ].max()

        if benefit_max > benefit_min:

            benefit_norm = (
                result[benefit]
                -
                benefit_min
            ) / (
                benefit_max
                -
                benefit_min
            )

        else:

            benefit_norm = pd.Series(
                0.0,
                index=result.index
            )

        if cost_max > cost_min:

            cost_norm = (
                result[cost]
                -
                cost_min
            ) / (
                cost_max
                -
                cost_min
            )

        else:

            cost_norm = pd.Series(
                0.0,
                index=result.index
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

    return result.head(
        top_n
    )