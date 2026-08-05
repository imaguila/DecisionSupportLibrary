import streamlit as st
from lenses import get_lens
from soi.soi_registry import load_soi

def render_diversity_lens_ui(df, available_columns):
    st.subheader("Lentes de Diversidad (Clustering)")

    method_key = st.selectbox(
        "Selecciona el Algoritmo de Clustering:",
        options=["kmedoids", "kmeans", "agglomerative", "hdbscan"],
        format_func=lambda x: {
            "kmedoids": "K-Medoids (Robusto)",
            "kmeans": "K-Means (Estándar)",
            "agglomerative": "Agrupamiento Jerárquico",
            "hdbscan": "HDBSCAN (Basado en Densidad)"
        }[x]
    )

    selected_features = st.multiselect(
        "Métricas/Variables para evaluar diversidad:",
        options=available_columns,
        default=available_columns[:2] if len(available_columns) >= 2 else available_columns
    )

    auto_k = st.checkbox("Modo Automático (Seleccionar K mediante Silhouette Score)", value=True)
    k_val = None if auto_k else st.slider("Número de Clústeres (k):", 2, 10, 3)

    if st.button("Ejecutar Clustering", use_container_width=True):
        lens = get_lens(method_key)
        
        # Ejecución independiente limpia
        groups = lens.run(
            df=df,
            feature_cols=selected_features,
            id_col="id",
            k=k_val,
            auto_k=auto_k
        )

        if groups:
            st.session_state["active_diversity_groups"] = groups
            st.success(f"Se han generado {len(groups)} grupos/clústeres distintos.")

    # Selección de un clúster individual para cargar como SOI
    groups = st.session_state.get("active_diversity_groups")
    if groups:
        selected_group = st.selectbox("Selecciona el clúster a inspeccionar/cargar:", list(groups.keys()))
        
        if st.button("Cargar Clúster Seleccionado como SOI Activo", use_container_width=True):
            soi_payload = {
                "name": f"SOI - {selected_group}",
                "ids": groups[selected_group],
                "lens": "Diversity",
                "method": method_key.upper(),
                "group": selected_group,
                "source_size": len(df),
            }
            load_soi(soi_payload)
            st.rerun()