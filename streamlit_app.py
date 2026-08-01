import streamlit as st

from ui.input_panel import render_input_panel
from core.framing import apply_framing
from core.workspace import render_workspace

st.set_page_config(
    page_title="Decision Space Explorer",
    layout="wide"
)

st.title("Decision Space Explorer")

dataset = render_input_panel()

if dataset is None:

    st.info(
        "Select a dataset to begin."
    )

    st.stop()

filtered_df = apply_framing(dataset)

render_workspace(
    filtered_df,
    dataset
)