def apply_efficiency_lens(
    df,
    benefit,
    cost,
    top_n
):

    result = df.copy()

    result["lens_score"] = (

        result[benefit]

        /

        (
            result[cost]
            + 1e-9
        )
    )

    result = result.sort_values(
        "lens_score",
        ascending=False
    )

    return result.head(top_n)