import streamlit as st
from lenses import get_lens
from soi.soi_registry import load_soi

def render_efficiency_lens_ui(df, numeric_columns):
    st.subheader("⚡ Lente de Eficiencia (Relación Beneficio / Coste)")

    if len(numeric_columns) < 2:
        st.warning("Se requieren al menos 2 métricas numéricas para calcular la eficiencia.")
        return

    col1, col2 = st.columns(2)

    with col1:
        method = st.selectbox(
            "Método de Eficiencia:",
            options=[
                "Benefit/Cost Ratio",
                "Normalized Ratio",
                "Distance to Ideal",
                "Composite Cost Ratio",
            ],
            help="Selecciona el método matemático para evaluar la relación beneficio-coste."
        )
        benefit_metric = st.selectbox("Métrica de Beneficio (a maximizar):", numeric_columns)

    cost_options = [c for c in numeric_columns if c != benefit_metric]

    with col2:
        if method == "Composite Cost Ratio":
            cost_metrics = st.multiselect(
                "Métricas de Coste (a minimizar):",
                cost_options,
                default=cost_options[:min(2, len(cost_options))]
            )
        else:
            selected_cost = st.selectbox("Métrica de Coste (a minimizar):", cost_options)
            cost_metrics = [selected_cost] if selected_cost else []

    top_n = st.slider("Número de soluciones eficientes a aislar (Top N):", 1, len(df), min(5, len(df)))

    if st.button("Ejecutar Análisis de Eficiencia", use_container_width=True):
        if not benefit_metric or not cost_metrics:
            st.error("Debes seleccionar métricas válidas de beneficio y coste.")
            return

        lens = get_lens("efficiency")
        groups = lens.run(
            df=df,
            benefit_col=benefit_metric,
            cost_cols=cost_metrics,
            method=method,
            top_n=top_n,
            id_col="id"
        )

        if groups:
            group_name = list(groups.keys())[0]
            st.success(f"Se han identificado las {len(groups[group_name])} soluciones más eficientes.")

            soi_payload = {
                "name": f"SOI - {group_name}",
                "ids": groups[group_name],
                "lens": "Efficiency",
                "method": method,
                "source_size": len(df),
            }
            load_soi(soi_payload)
            st.rerun()