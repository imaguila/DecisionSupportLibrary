## --------------------------------------------------------------------------------------
## lens_preference.py
## --------------------------------------------------------------------------------------

import pandas as pd


def apply_preference_lens(
    df,
    method,
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

    # ==================================================
    # WEIGHTED SUM
    # ==================================================

    if method == "Weighted Sum":

        score = pd.Series(
            0.0,
            index=result.index
        )

        for metric in criteria:

            mi = result[metric].min()
            ma = result[metric].max()

            if ma > mi:

                norm = (
                    result[metric]
                    -
                    mi
                ) / (
                    ma
                    -
                    mi
                )

            else:

                norm = pd.Series(
                    0.0,
                    index=result.index
                )

            if metric in maximize:

                score = score + norm

            else:

                score = score + (
                    1.0 - norm
                )

        result[
            "preference_score"
        ] = score

    # ==================================================
    # TOPSIS
    # ==================================================

    elif method == "TOPSIS":

        norm_df = result[
            criteria
        ].copy()

        for metric in criteria:

            denom = (
                norm_df[metric] ** 2
            ).sum() ** 0.5

            if denom != 0:

                norm_df[metric] = (
                    norm_df[metric]
                    /
                    denom
                )

            else:

                norm_df[metric] = 0.0

        ideal = {}
        anti_ideal = {}

        for metric in criteria:

            if metric in maximize:

                ideal[metric] = (
                    norm_df[metric].max()
                )

                anti_ideal[metric] = (
                    norm_df[metric].min()
                )

            else:

                ideal[metric] = (
                    norm_df[metric].min()
                )

                anti_ideal[metric] = (
                    norm_df[metric].max()
                )

        d_plus = []
        d_minus = []

        for _, row in norm_df.iterrows():

            dp = sum(
                (
                    row[metric]
                    -
                    ideal[metric]
                ) ** 2
                for metric in criteria
            ) ** 0.5

            dm = sum(
                (
                    row[metric]
                    -
                    anti_ideal[metric]
                ) ** 2
                for metric in criteria
            ) ** 0.5

            d_plus.append(
                dp
            )

            d_minus.append(
                dm
            )

        result[
            "preference_score"
        ] = [
            (
                dm / (dp + dm)
                if (dp + dm) != 0
                else 0.0
            )
            for dp, dm in zip(
                d_plus,
                d_minus
            )
        ]

    # ==================================================
    # UNKNOWN METHOD
    # ==================================================

    else:

        return result

    # ==================================================
    # RANKING AND SELECTION
    # ==================================================

    result = result.sort_values(
        "preference_score",
        ascending=False
    ).copy()

    result[
        "preference_rank"
    ] = range(
        1,
        len(result) + 1
    )

    return result.head(
        top_n
    )