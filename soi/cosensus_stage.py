import streamlit as st
from lenses import get_lens
from soi.soi_registry import load_soi

def render_consensus_lens_ui(df):
    st.subheader("🤝 Lente de Consenso (Combinación de SOIs)")

    # Recuperar SOIs guardados previamente en la sesión
    saved_sois = st.session_state.get("saved_sois", [])

    if len(saved_sois) < 2:
        st.info("Se requieren al menos 2 SOIs guardados previamente para realizar un análisis de consenso.")
        return

    soi_names = [soi["name"] for soi in saved_sois if "name" in soi]

    col1, col2 = st.columns(2)

    with col1:
        method = st.selectbox(
            "Regla de Consenso:",
            options=["Consensus Threshold", "Union", "Majority", "Intersection"],
            help="Determina el nivel de acuerdo requerido entre los SOIs seleccionados."
        )

    with col2:
        selected_soi_names = st.multiselect(
            "SOIs a Combinar:",
            options=soi_names,
            default=soi_names[:min(2, len(soi_names))]
        )

    threshold_val = 0.5
    if method == "Consensus Threshold":
        threshold_val = st.slider(
            "Nivel de Acuerdo Mínimo (Umbral):",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="0.5 exige que la solución esté en al menos el 50% de los SOIs."
        )

    if st.button("Generar SOI de Consenso", use_container_width=True):
        if len(selected_soi_names) < 2:
            st.error("Por favor selecciona al menos 2 SOIs para combinar.")
            return

        # Mapear los nombres de SOIs seleccionados a sus listas de IDs
        soi_dict_map = {
            soi["name"]: soi.get("ids", [])
            for soi in saved_sois
            if soi.get("name") in selected_soi_names
        }

        lens = get_lens("consensus")
        groups = lens.run(
            df=df,
            soi_dict_map=soi_dict_map,
            method=method,
            threshold=threshold_val,
            id_col="id"
        )

        if groups:
            group_name = list(groups.keys())[0]
            st.success(f"Consenso generado con éxito: {len(groups[group_name])} soluciones resultantes.")

            soi_payload = {
                "name": f"SOI - {group_name}",
                "ids": groups[group_name],
                "lens": "Consensus",
                "method": method,
                "source_sois": selected_soi_names,
            }
            load_soi(soi_payload)
            st.rerun()
        else:
            st.warning("Ninguna solución cumple con el nivel de consenso requerido.")