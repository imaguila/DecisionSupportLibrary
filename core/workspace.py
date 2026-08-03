## --------------------------------------------------------------------------------------
## workspace.py
## --------------------------------------------------------------------------------------

import streamlit as st

from core.workspace_summary import (
        render_summary )
from core.workspace_maps import (
    render_maps )
from core.workspace_dataset import (
    render_dataset_preview )
from soi.soi_registry import (
    render_soi_registry )

def render_workspace( df, dataset,  show_ids) :

    if df is None:
        st.error( "No dataset is available for the workspace." )
        return

    dimensions = ( dataset["metrics"] +
        dataset["selected_indicators"] )

    render_summary( df, dataset )

    if len(dimensions) < 2:
        st.warning(
            "At least two dimensions are required "
            "to render decision-space maps."
        )

        render_soi_registry()
        render_dataset_preview( df, dataset )

        return

    render_maps( df, dataset, dimensions, show_ids )
    render_soi_registry()
    render_dataset_preview( df, dataset )