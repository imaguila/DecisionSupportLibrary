# input_panel.py
import streamlit as st
import pandas as pd
from config import CASES
from problem import run_pipeline, leer_soluciones
from enrichment import detectar_indicadores_posibles, aplicar_enrichment


def render_input_panel():
    """Render the input and preparation sidebar panel."""

    st.sidebar.markdown(
        "## 🏷️ Input and Preparation",
        help="Load precomputed Pareto fronts or run internal benchmark cases."
    )

    # Title and reset button layout
    col_texto, col_btn = st.sidebar.columns([2, 1.5], vertical_alignment="center")

    with col_texto:
        st.markdown(
            "Select data source",
            help="• Load custom dataset: Upload any external CSV file containing Pareto solutions.\n\n• Benchmark cases: Select pre-configured domain case studies."
        )

    with col_btn:
        if st.button("🔄 Reset data", use_container_width=True):
            st.session_state.clear()
            st.success("Reset ✔️")
            st.rerun()

    data_mode = st.sidebar.radio(
        "Select data source",
        [
            "📂 Load custom dataset",
            "📥 Benchmark cases"
        ],
        label_visibility="collapsed",
    )

    # ============================================
    # 1) CUSTOM DATASET UPLOAD MODE
    # ============================================
    if data_mode == "📂 Load custom dataset":
        uploaded_file = st.sidebar.file_uploader("Upload dataset (CSV)", type=["csv"])

        if uploaded_file is None:
            st.warning("Please upload a CSV file containing solutions and decision variables.")
            st.stop()

        df = pd.read_csv(uploaded_file)

        if "id" not in df.columns:
            df["id"] = range(1, len(df) + 1)

        st.sidebar.success(f"{len(df)} solutions loaded")

        # Dynamic indicator enrichment for uploaded data
        possible_indicators = detectar_indicadores_posibles(df)

        if possible_indicators:
            st.sidebar.markdown("## 🎨 Semantic enrichment")
            selected_indicators = st.sidebar.multiselect(
                "Indicators",
                possible_indicators,
                default=[],
                help="Select domain indicators to compute based on uploaded base metrics."
            )
            df = aplicar_enrichment(df, selected_indicators)

        st.session_state["matriz_solicitud"] = None
        return df

    # ============================================
    # 2) BENCHMARK CASES MODE (PRE-CONFIGURED DATA)
    # ============================================
    st.sidebar.markdown(
        "## 🎨 Semantic Enrichment",
        help="Dynamically compute domain indicators for the selected benchmark case."
    )

    lista_casos = list(CASES.keys())

    # Get selected case study
    case_actual = st.session_state.get("case_selector", lista_casos[0])
    texto_ayuda = CASES[case_actual].get("help", "No bibliographic reference available.")

    case_name = st.sidebar.selectbox(
        "Benchmark Case Study",
        lista_casos,
        key="case_selector",
        help=texto_ayuda
    )

    config = CASES[case_name]
    df_base = leer_soluciones(config)

    available_indicators = detectar_indicadores_posibles(df_base)
    default_indicators = config.get("default_indicators", [])

    selected_indicators = st.sidebar.multiselect(
        "Indicators",
        available_indicators,
        default=[i for i in default_indicators if i in available_indicators],
        key="indicators_selector",
        help="Select derived domain indicators to compute dynamically."
    )

    @st.cache_data
    def build_case_df(name, selected_inds):
        return run_pipeline(name, selected_inds)

    df, matriz_solicitud = build_case_df(case_name, selected_indicators)

    # Store prefix and request matrix in session state for downstream visualizations
    st.session_state["matriz_solicitud"] = matriz_solicitud
    st.session_state["var_prefix"] = config.get("var_prefix", "req_")

    st.sidebar.success(f"{len(df)} benchmark solutions enriched")

    return df