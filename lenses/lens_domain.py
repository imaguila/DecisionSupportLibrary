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