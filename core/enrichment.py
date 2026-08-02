import streamlit as st


def render_enrichment(
    dataset
):

    plugin = dataset["plugin"]

    if plugin is None:

        dataset["selected_indicators"] = []

        return dataset

    selected_metrics = dataset["metrics"]

    available_indicators = []

    requirements = (
        plugin.requirements()
    )

    for indicator, reqs in requirements.items():

        if all(
            metric in selected_metrics
            for metric in reqs
        ):

            available_indicators.append(
                indicator
            )

    with st.sidebar.expander(
        "⚙️ Data Enrichment",
        expanded=False
    ):

        st.caption(
            f"ℹ️ Detected {len(available_indicators)} indicators based on active plugin and config."
        )

        selected_indicators = st.multiselect(
            "Avalible candidates for enrichement",
            sorted(
                available_indicators
            ),
            default=[
                i
                for i in dataset["config"].get(
                    "default_indicators",
                    []
                )
                if i in available_indicators
            ],
            help=""" 💡Select  to enrich the current
decision space.  Only indicators compatible with the selected objectives
and supported by the active plugin are available.
"""
        )

    dataset["df"] = plugin.compute_indicators(
        dataset["df"],
        selected_indicators
    )

    dataset[
        "selected_indicators"
    ] = selected_indicators

    return dataset