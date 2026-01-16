import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Centro de Mando: Escudo Pyme",
    page_icon="🛡️",
    layout="wide"
)

# Refresco automático cada 60 segundos
st_autorefresh(interval=60000, key="datarefresh")

# --- 2. CARGA DE DATOS ---
# Reemplaza con tu URL de Google Sheets publicada como CSV
SHEET_URL = "TU_URL_AQUI"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # Limpieza básica de columnas
        df.columns = [c.strip().capitalize() for c in df.columns]
        
        # Asegurar que las columnas necesarias existan
        required = ['Fecha', 'Emisor', 'Monto', 'Veredicto', 'Analisis', 'Confianza']
        for col in required:
            if col not in df.columns:
                df[col] = "N/A"
        
        # Formatear Monto como número
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# --- 3. ENCABEZADO Y FILTROS ---
st.title("🛡️ Centro de Mando: Escudo Pyme")
st.markdown("---")

if df.empty:
    st.warning("⚠️ No se encontraron datos. Verifica que el flujo de n8n haya procesado su primera factura.")
    st.stop()

# --- 4. KPIs PRINCIPALES (Métricas de Valor) ---
total_analizados = len(df)
amenazas = len(df[df['Veredicto'].isin(['FRAUDE', 'RIESGOSO'])])
capital_protegido = df[df['Veredicto'] == 'FRAUDE']['Monto'].sum()
verificados = len(df[df['Confianza'] == 'ALTA'])

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Documentos Analizados", total_analizados)
with col2:
    st.metric("Alertas Detectadas", amenazas, delta_color="inverse")
with col3:
    st.metric("Capital Protegido", f"$ {capital_protegido:,.0f}".replace(",", "."))
with col4:
    st.metric("Confianza de Red (Lista Blanca)", f"{verificados}", "🛡️ Verificados")

st.markdown("---")

# --- 5. GRÁFICOS Y ANÁLISIS ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 Historial de Amenazas por Fecha")
    # Agrupar por fecha para el gráfico
    df['Fecha_dt'] = pd.to_datetime(df['Fecha']).dt.date
    chart_data = df.groupby(['Fecha_dt', 'Veredicto']).size().reset_index(name='Cantidad')
    fig_line = px.line(chart_data, x='Fecha_dt', y='Cantidad', color='Veredicto',
                       markers=True, color_discrete_map={
                           'VERIFICADO': '#2ecc71',
                           'RIESGOSO': '#f1c40f',
                           'FRAUDE': '#e74c3c'
                       })
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.subheader("🎯 Estado de Riesgo")
    fig_pie = px.pie(df, names='Veredicto', hole=0.6,
                     color='Veredicto',
                     color_discrete_map={
                           'VERIFICADO': '#2ecc71',
                           'RIESGOSO': '#f1c40f',
                           'FRAUDE': '#e74c3c'
                     })
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 6. REGISTRO DETALLADO (AUDITORÍA FORENSE) ---
st.subheader("📋 Auditoría Forense en Tiempo Real")

# Aplicar estilos de color a la tabla
def highlight_veredicto(val):
    color = 'white'
    if val == 'FRAUDE': color = '#ff4b4b'
    elif val == 'RIESGOSO': color = '#ffa500'
    elif val == 'VERIFICADO': color = '#28a745'
    return f'background-color: {color}; color: white; font-weight: bold'

st.dataframe(
    df[['Fecha', 'Emisor', 'Monto', 'Veredicto', 'Confianza', 'Analisis']]
    .sort_index(ascending=False)
    .style.applymap(highlight_veredicto, subset=['Veredicto']),
    use_container_width=True
)

st.markdown("---")
st.caption("🛡️ Escudo Pyme v2.0 | Sistema de Vigilancia Activa conforme a la Ley Marco de Ciberseguridad.")