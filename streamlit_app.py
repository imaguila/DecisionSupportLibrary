import streamlit as st
import pandas as pd

from input_panel import render_input_panel
from metrics_catalog import get_metric_sets

# --------------------------------------------
# CONFIGURACIÓN BÁSICA
# --------------------------------------------
st.set_page_config(layout="wide", page_title="Input Panel Test")
st.title("🧪 Decision Space Explorer - Input Test")

DATA_PATH = "data"

st.markdown("---")

# --------------------------------------------
# 1. PANEL DE ENTRADA (Carga de datos)
# --------------------------------------------
st.subheader("1. Carga de Datos")

# Invocamos la función del panel de entrada
df = render_input_panel()

# --------------------------------------------
# 2. VALIDACIÓN Y MÉTRICAS
# --------------------------------------------
st.markdown("---")
st.subheader("2. Verificación de Datos e Indicadores")

if df is not None and not df.empty:
    st.success(f"✅ ¡Datos cargados correctamente! Se han obtenido **{len(df)}** filas (soluciones) y **{len(df.columns)}** columnas.")

    # Obtenemos las métricas detectadas/disponibles
    available_opt, available_qual, available_metrics = get_metric_sets(df, DATA_PATH)

    # Mostramos resumen en métricas de Streamlit
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Objetivos Optimización", len(available_opt))
    with col2:
        st.metric("Indicadores de Calidad", len(available_qual))
    with col3:
        st.metric("Total Métricas Disponibles", len(available_metrics))

    # Desplegables rápidos para inspeccionar los nombres de las métricas
    with st.expander("🔍 Ver listado de métricas detectadas", expanded=True):
        st.write("**Optimización:**", available_opt)
        st.write("**Calidad:**", available_qual)
        st.write("**Totales:**", available_metrics)

    # --------------------------------------------
    # 3. PREVIEW DE LA TABLA COMPLETA
    # --------------------------------------------
    st.markdown("---")
    st.subheader("3. Vista previa del DataFrame (Primeras 50 filas)")
    st.dataframe(df.head(50), use_container_width=True)

else:
    st.warning("⚠️ No se ha cargado ningún DataFrame aún. Revisa la configuración en el panel de la izquierda.")