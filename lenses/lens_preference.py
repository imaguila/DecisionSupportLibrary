## --------------------------------------------------------------------------------------
## lenses_preference.py


import pandas as pd

def apply_preference_lens(
    df,
    method,
    maximize,
    minimize,
    top_n
):

    criteria = maximize + minimize

    if not criteria:

        return df

    df_temp = df.copy()

    # =====================================
    # WEIGHTED SUM
    # =====================================

    if method == "Weighted Sum":

        score = 0

        for metric in criteria:

            mi = df_temp[metric].min()
            ma = df_temp[metric].max()

            if ma > mi:

                norm = (
                    df_temp[metric] - mi
                ) / (
                    ma - mi
                )

            else:

                norm = 0

            if metric in maximize:

                score += norm

            else:

                score -= norm

        df_temp["preference_score"] = score

        score_col = "preference_score"

    # =====================================
    # TOPSIS
    # =====================================

    else:

        norm_df = df_temp[
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

        for i in range(
            len(norm_df)
        ):

            row = norm_df.iloc[i]

            dp = sum(

                (
                    row[m]
                    -
                    ideal[m]
                ) ** 2

                for m in criteria

            ) ** 0.5

            dm = sum(

                (
                    row[m]
                    -
                    anti_ideal[m]
                ) ** 2

                for m in criteria

            ) ** 0.5

            d_plus.append(
                dp
            )

            d_minus.append(
                dm
            )

        df_temp[
            "preference_score"
        ] = [

            dm / (dp + dm)
            if (dp + dm) != 0
            else 0
            for dp, dm in zip(
                d_plus,
                d_minus
            )
        ]
        score_col = (
            "preference_score"
        )

    result = (
        df_temp
        .sort_values(
            score_col,
            ascending=False
        )
        .head(top_n)
    )

    return result