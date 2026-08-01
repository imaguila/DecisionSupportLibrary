"""
Generic enrichment layer.

The core framework does not know how indicators are calculated.
Indicator computation is delegated to the active domain plugin.
"""


def detect_available_indicators(plugin):
    """
    Returns the indicators exposed by the active plugin.
    """

    if plugin is None:
        return []

    return sorted(
        list(
            plugin.available_indicators()
        )
    )


def apply_enrichment(
    df,
    plugin,
    selected_indicators
):
    """
    Delegates indicator computation to the active plugin.
    """

    if plugin is None:
        return df

    if not selected_indicators:
        return df

    return plugin.compute_indicators(
        df,
        selected_indicators
    )