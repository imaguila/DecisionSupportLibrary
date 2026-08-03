from core.workspace_summary import (
    render_summary
)
from core.workspace_controls import (
    render_workspace_controls
)
from core.workspace_maps import (
    render_maps
)
from core.workspace_dataset import (
    render_dataset_preview
)
from soi.soi_registry import (
    render_soi_registry
)

def render_workspace(
    df,
    dataset,
    show_ids
):

    render_summary(
        df,
        dataset
    )

    dimensions = (

        dataset["metrics"]

        +

        dataset["selected_indicators"]

    )

    if len(dimensions) < 2:
        return

    render_maps(
        df,
        dataset,
        dimensions,
        show_ids
    )
    render_soi_registry()
    render_dataset_preview(
        df,
        dataset
    )