import streamlit as st

from input_panel import (
    render_input_panel
)

st.set_page_config(
    page_title="Decision Space Explorer",
    layout="wide"
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

cfg = dataset["config"]

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
        "Attributes",
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

st.caption(
    "Detected decision-variable prefix: "
    f"`{cfg.get('var_prefix', 'N/A')}`"
)

# ==================================================
# ANALYSIS DIMENSIONS
# ==================================================

st.subheader(
    "Available Analysis Dimensions"
)

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        "#### Optimization Objectives"
    )

    metrics = dataset.get(
        "metrics",
        []
    )

    if metrics:

        for m in metrics:
            st.markdown(
                f"✅ {m}"
            )

    else:

        st.info(
            "No objectives defined."
        )

with col2:

    st.markdown(
        "#### Active Enrichment Indicators"
    )

    indicators = dataset.get(
        "selected_indicators",
        []
    )

    if indicators:

        for i in indicators:

            st.markdown(
                f"✅ {i}"
            )

    else:

        st.info(
            "No indicators enabled."
        )

# ==================================================
# DATA PREVIEW
# ==================================================

st.subheader(
    "Data Preview"
)

st.dataframe(
    df,
    use_container_width=True,
    height=500
)