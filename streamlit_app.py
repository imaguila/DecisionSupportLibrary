import streamlit as st

from input_panel import (
    render_input_panel
)

st.set_page_config(
    layout="wide",
    page_title="Decision Space Explorer"
)

st.title(
    "Decision Space Explorer"
)

dataset = render_input_panel()

if dataset is None:

    st.info(
        "Select a dataset to begin."
    )

    st.stop()

df = dataset["df"]

# ==================================================
# SUMMARY
# ==================================================

st.subheader(
    "Dataset Summary"
)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Solutions",
        len(df)
    )

with c2:
    st.metric(
        "Columns",
        len(df.columns)
    )

with c3:
    st.metric(
        "Decision Variables",
        len(
            dataset[
                "decision_variables"
            ]
        )
    )

# ==================================================
# METRICS
# ==================================================

st.subheader(
    "Detected Structure"
)

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        "### Metrics"
    )

    st.write(
        dataset["metrics"]
    )

with col2:

    st.markdown(
        "### Decision Variables"
    )

    st.write(
        dataset[
            "decision_variables"
        ][:20]
    )

# ==================================================
# ENRICHMENT
# ==================================================

plugin = dataset["plugin"]

if plugin:

    st.subheader(
        "Applied Indicators"
    )

    st.write(
        plugin.available_indicators()
    )

# ==================================================
# PREVIEW
# ==================================================

st.subheader(
    "Data Preview"
)

st.dataframe(
    df.head(50),
    use_container_width=True
)

# ==================================================
# RAW COLUMNS
# ==================================================

with st.expander(
    "Column Inspector"
):

    st.write(
        list(df.columns)
    )