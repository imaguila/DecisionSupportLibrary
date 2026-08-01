"""
Generic enrichment layer.

Indicator computation is delegated
to the active domain plugin.
"""


def detect_available_indicators(plugin):

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

    if plugin is None:
        return df

    if not selected_indicators:
        return df

    return plugin.compute_indicators(
        df,
        selected_indicators
    )