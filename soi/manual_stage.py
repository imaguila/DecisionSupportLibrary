import streamlit as st
from lenses import get_lens
from soi.soi_registry import load_soi

def render_manual_lens_ui(df: pd.DataFrame, id_col: str = "id"):
    st.subheader("📌 Lente de Selección Manual")

    if df is None or df.empty or id_col not in df.columns:
        st.warning("No hay soluciones disponibles para selección manual.")
        return

    valid_ids = df[id_col].dropna().tolist()

    selected_ids = st.multiselect(
        "Selecciona soluciones por ID:",
        options=valid_ids,
        default=[],
        help="Elige manualmente las soluciones exactas que deseas aislar como un Subespacio de Interés (SOI)."
    )

    if st.button("Aislar Selección Manual", use_container_width=True):
        lens = get_lens("manual")
        groups = lens.run(df=df, selected_ids=selected_ids, id_col=id_col)

        if groups:
            group_name = list(groups.keys())[0]
            st.success(f"Selección activa: **{len(selected_ids)}** solución(es) aisladas.")
            
            # Carga automática del subespacio a la memoria SOI
            soi_payload = {
                "name": f"SOI - {group_name}",
                "ids": groups[group_name],
                "lens": "Manual",
                "method": "MANUAL",
                "source_size": len(df),
            }
            load_soi(soi_payload)
            st.rerun()
        else:
            st.caption("No se ha seleccionado ninguna solución válida.")