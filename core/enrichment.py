## --------------------------------------------------------------------------------------
## core/enrichment.py
## --------------------------------------------------------------------------------------

import streamlit as st

def get_available_indicators( plugin, selected_metrics ):
    available_indicators = []
    requirements = plugin.requirements()
    for indicator, reqs in requirements.items():
        if all( metric in selected_metrics for metric in reqs ):
            available_indicators.append( indicator )
    return available_indicators

def render_enrichment( dataset ):
    plugin = dataset[ "plugin" ]
    if plugin is None:
        dataset[ "selected_indicators" ] = []
        return dataset

    selected_metrics = dataset[ "metrics" ]
    available_indicators = get_available_indicators(
        plugin, selected_metrics )

    with st.sidebar.expander( "⚙️ Data Enrichment", expanded=False ):
        st.caption(
            f"Detected {len(available_indicators)} "
            "compatible indicators." )

        selected_indicators = st.multiselect(
            "Available indicators",
            sorted( available_indicators ),
            default=[
                indicator
                for indicator in dataset[
                    "config"
                ].get(
                    "default_indicators",
                    []
                )
                if indicator in available_indicators
            ],
            help=(
                "Select indicators to enrich the current "
                "decision space. Only indicators compatible "
                "with the selected objectives and active plugin "
                "are available."
            )
        )

    dataset[ "df"] = plugin.compute_indicators(
        dataset[ "df" ],
        selected_indicators
    )
    
    dataset[ "selected_indicators" ] = selected_indicators

    return dataset