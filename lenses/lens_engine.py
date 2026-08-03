## --------------------------------------------------------------------------------------
## lens_engine.py
## --------------------------------------------------------------------------------------

from lenses.lens_preference import (
    apply_preference_lens
)

from lenses.lens_diversity import (
    apply_diversity_lens
)

from lenses.lens_efficiency import (
    apply_efficiency_lens
)

from lenses.lens_domain import (
    apply_domain_lens
)


def apply_lens(
    df,
    lens_name,
    params,
    dataset
):

    if df is None:

        return df

    if lens_name == "None":

        return df.copy()

    # ==================================================
    # Preference Lens
    # ==================================================

    if lens_name == "Preference":

        return apply_preference_lens(
            df,
            params.get(
                "method",
                "Weighted Sum"
            ),
            params.get(
                "maximize",
                []
            ),
            params.get(
                "minimize",
                []
            ),
            params.get(
                "top_n",
                len(df)
            )
        )

    # ==================================================
    # Diversity Lens
    # ==================================================

    if lens_name == "Diversity":

        dimensions = (
            dataset["metrics"]
            +
            dataset["selected_indicators"]
        )

        return apply_diversity_lens(
            df,
            dimensions,
            params
        )

    # ==================================================
    # Efficiency Lens
    # ==================================================

    if lens_name == "Efficiency":

        return apply_efficiency_lens(
            df,
            params.get(
                "method",
                "Benefit/Cost Ratio"
            ),
            params.get(
                "benefit"
            ),
            params.get(
                "cost"
            ),
            params.get(
                "top_n",
                len(df)
            )
        )

    # ==================================================
    # Indicator Dominance Lens
    # ==================================================

    if lens_name == "Indicator Dominance":

        return apply_domain_lens(
            df,
            params.get(
                "maximize",
                []
            ),
            params.get(
                "minimize",
                []
            ),
            params.get(
                "top_n",
                len(df)
            )
        )

    return df.copy()