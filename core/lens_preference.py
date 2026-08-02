import pandas as pd

def apply_preference_lens(
    df,
    maximize,
    minimize,
    top_n
):

    result = df.copy()
    score = 0
    for metric in maximize:
        if metric in result.columns:
            norm = (
                result[metric]
                - result[metric].min()
            ) / (
                result[metric].max()
                - result[metric].min()
                + 1e-9
            )
            score += norm

    for metric in minimize:
        if metric in result.columns:
            norm = (
                result[metric]
                - result[metric].min()
            ) / (
                result[metric].max()
                - result[metric].min()
                + 1e-9
            )

            score -= norm

    result["lens_score"] = score
    result = result.sort_values(
        "lens_score",
        ascending=False
    )

    return result.head(top_n)