import streamlit as st
from lenses import get_lens
from soi.soi_registry import load_soi

def render_indicator_lens_ui(df, available_indicators):
    st.subheader("📊 Lente de Indicadores y Frente de Pareto")

    if not available_indicators:
        st.warning("No hay indicadores o métricas disponibles para la evaluación.")
        return

    method = st.selectbox(
        "Método de Indicadores:",
        options=["Top-N Matches", "Non-dominated"],
        help="Top-N Matches agrupa por coincidencias en dimensiones individuales. Non-dominated aísla la Frontera de Pareto."
    )

    col1, col2 = st.columns(2)
    with col1:
        maximize_cols = st.multiselect("Indicadores a Maximizar:", available_indicators)
    with col2:
        minimize_options = [c for c in available_indicators if c not in maximize_cols]
        minimize_cols = st.multiselect("Indicadores a Minimizar:", minimize_options)

    top_n_val = 5
    if method == "Top-N Matches":
        top_n_val = st.slider("Top N por dimensión:", 1, len(df), min(5, len(df)))

    if st.button("Ejecutar Análisis de Indicadores", use_container_width=True):
        if not maximize_cols and not minimize_cols:
            st.error("Debes seleccionar al menos un indicador para maximizar o minimizar.")
            return

        lens = get_lens("indicator")
        groups = lens.run(
            df=df,
            maximize=maximize_cols,
            minimize=minimize_cols,
            method=method,
            top_n=top_n_val,
            id_col="id"
        )

        if groups:
            st.session_state["active_indicator_groups"] = groups
            st.success(f"Se han identificado {len(groups)} categoría(s) de coincidencias/Pareto.")

    groups = st.session_state.get("active_indicator_groups")
    if groups:
        selected_group = st.selectbox("Selecciona la categoría a aislar como SOI:", list(groups.keys()))
        
        if st.button("Cargar Categoría Seleccionada como SOI Activo", use_container_width=True):
            soi_payload = {
                "name": f"SOI - {selected_group}",
                "ids": groups[selected_group],
                "lens": "Indicator",
                "method": method,
                "group": selected_group,
                "source_size": len(df),
            }
            load_soi(soi_payload)
            st.rerun()