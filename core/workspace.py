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

   # show_ids = (
   #     render_workspace_controls(
   #         dimensions
   #     )
   # )

    render_maps(
        df,
        dataset,
        dimensions,
        show_ids
    )

    render_dataset_preview(
        df,
        dataset
    )