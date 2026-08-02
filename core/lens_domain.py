def apply_domain_lens(
    df,
    indicators,
    top_n
):

    result = df.copy()

    if len(indicators) == 0:
        return result

    score = 0

    for indicator in indicators:
        if indicator not in result.columns:
            continue

        norm = (
            result[indicator]
            -
            result[indicator].min()

        ) / (

            result[indicator].max()
            -
            result[indicator].min()
            +
            1e-9
        )

        score += norm

    result["lens_score"] = score
    result = result.sort_values(
        "lens_score",
        ascending=False
    )

    return result.head(top_n)