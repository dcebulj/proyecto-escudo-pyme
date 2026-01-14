import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Escudo Pyme - Dashboard", layout="wide")

# 1. PEGA TU ENLACE CSV AQUÍ
# Asegúrate que termine en &output=csv o similar
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTlSH-jwfLUINNaWhCNb88mAoLjUAlQzkqqZNwLG7tteMQof1yis0bFoieF2FVvOniS0MRIsAGWpXgb/pub?gid=0&single=true&output=csv"

st.title("🛡️ Centro de Mando: Escudo Pyme")
st.markdown("---")

# --- CARGA DE DATOS CON MANEJO DE ERRORES ---
def load_data():
    try:
        # Leemos el CSV
        df = pd.read_csv(SHEET_URL)
        
        # Limpieza básica de nombres de columnas (quitar espacios)
        df.columns = df.columns.str.strip()
        
        # Convertir Fecha a formato fecha
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
            
        # Convertir Monto a número (limpiando cualquier texto sobrante)
        if 'Monto' in df.columns:
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        st.error(f"❌ Error al conectar con los datos: {e}")
        return pd.DataFrame()

df = load_data()

# --- VALIDACIÓN DE DATOS ---
if df.empty:
    st.warning("⚠️ No se encontraron datos. Verifica que el enlace CSV sea correcto y tenga datos.")
    # Mostramos un ejemplo de cómo debería ser el link
    st.info("El link debe verse similar a: https://docs.google.com/spreadsheets/d/e/.../pub?output=csv")
else:
    # --- MÉTRICAS PRINCIPALES ---
    col1, col2, col3 = st.columns(3)
    
    total_docs = len(df)
    amenazas = len(df[df['Veredicto'].str.contains('VERIFICAR|RIESGOSO', case=False, na=False)])
    capital = df[df['Veredicto'].str.contains('VERIFICAR|RIESGOSO', case=False, na=False)]['Monto'].sum()

    col1.metric("Docs Analizados", total_docs)
    col2.metric("Amenazas Detectadas", amenazas, delta_color="inverse")
    col3.metric("Capital Protegido", f"$ {capital:,.0f}".replace(",", "."))

    st.markdown("---")

    # --- GRÁFICOS ---
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("📊 Historial de Análisis")
        # Agrupar por fecha si existe
        if 'Fecha' in df.columns:
            df_daily = df.groupby([df['Fecha'].dt.date, 'Veredicto']).size().reset_index(name='Cantidad')
            fig = px.bar(df_daily, x='Fecha', y='Cantidad', color='Veredicto', barmode='group',
                         color_discrete_map={'SEGURO': '#00CC96', 'VERIFICAR': '#EF553B', 'RIESGOSO': '#EF553B'})
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🛡️ Estado de Riesgo")
        fig_pie = px.pie(df, names='Veredicto', hole=0.4,
                         color='Veredicto',
                         color_discrete_map={'SEGURO': '#00CC96', 'VERIFICAR': '#EF553B', 'RIESGOSO': '#EF553B'})
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- TABLA DETALLADA ---
    st.subheader("📋 Registro Detallado")
    st.dataframe(df.sort_values(by='Fecha', ascending=False) if 'Fecha' in df.columns else df, use_container_width=True)