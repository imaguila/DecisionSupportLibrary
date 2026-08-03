## --------------------------------------------------------------------------------------
## lenses_engine.py

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
    if lens_name == "None":
        return df
    
    if lens_name == "Preference":
        return apply_preference_lens(
            df,
            params["method"],
            params["maximize"],
            params["minimize"],
            params["top_n"]
        )

    if lens_name == "Efficiency":
        return apply_efficiency_lens(
            df,
            params["benefit"],
            params["cost"],
            params["top_n"]
        )

    if lens_name == "Domain-Specific":
        return apply_domain_lens(
            df,
            params["maximize"],
            params["minimize"],
            params["top_n"]
        )
    
    if lens_name == "Diversity":
        dimensions = (
            dataset["metrics"]
            +
            dataset["selected_indicators"]
        )

        return apply_diversity_lens(
            df,
            dimensions,
            params["target_size"]
        )

    return df