import streamlit as st

from core.input_panel import render_input_panel
from core.enrichment import render_enrichment
from core.framing import apply_framing
from core.workspace_controls import render_workspace_controls
from core.workspace import render_workspace

from lenses.lenses import render_lens_panel
from lenses.lens_engine import apply_lens
from lenses.lens_feedback import render_lens_feedback


st.set_page_config(
    page_title="Decision Space Explorer",
    layout="wide"
)

st.markdown(
    """
    <style>
    [data-testid="stExpander"] details summary p {
        font-size: 1.2rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title(
    "Decision Space Explorer"
)


dataset = render_input_panel()

if dataset is None:
    st.info(
        "Select a domain configuration to begin."
    )
    st.stop()


dataset = render_enrichment(
    dataset
)

dimensions = (
    dataset["metrics"]
    +
    dataset["selected_indicators"]
)

show_ids = render_workspace_controls(
    dimensions
)

framed_df = apply_framing(
    dataset
)

working_df = framed_df.copy()

if "active_soi_ids" in st.session_state:

    working_df = working_df[
        working_df["id"].isin(
            st.session_state.active_soi_ids
        )
    ].copy()


if st.session_state.get(
    "pending_lens_reset",
    False
):

    st.session_state[
        "active_lens"
    ] = "None"

    st.session_state[
        "pending_lens_reset"
    ] = False


active_lens, lens_params, feedback_placeholder = render_lens_panel(
    dataset,
    working_df
)

lens_df = apply_lens(
    working_df,
    active_lens,
    lens_params,
    dataset
)

if lens_df is None:

    st.sidebar.warning(
        "The selected lens returned no dataset. "
        "Reverting to the current working dataset."
    )

    lens_df = working_df.copy()


render_lens_feedback(
    feedback_placeholder,
    active_lens,
    lens_df
)


if "pending_save_soi" in st.session_state:

    if "saved_sois" not in st.session_state:

        st.session_state.saved_sois = []

    pending = st.session_state.pending_save_soi

    existing_names = [
        soi["name"]
        for soi in st.session_state.saved_sois
    ]

    if pending["name"] in existing_names:

        st.sidebar.warning(
            "A SOI with this name already exists."
        )

    else:

        st.session_state.saved_sois.append(
            {
                "name": pending["name"],
                "lens": pending["lens"],
                "params": pending.get(
                    "params",
                    {}
                ),
                "ids": lens_df["id"].tolist()
            }
        )

        st.sidebar.success(
            f"Saved SOI: {pending['name']}"
        )

    del st.session_state[
        "pending_save_soi"
    ]

render_workspace(
    lens_df,
    dataset,
    show_ids
)