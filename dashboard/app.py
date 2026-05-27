import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dashboard.utils import load_catalog, load_metricas

st.set_page_config(
    page_title="Analisis de Contenido Streaming",
    page_icon=None,
    layout="wide",
)

st.title("Analisis de Contenido en Plataformas de Streaming")
st.caption("15,000 titulos de 10 plataformas — periodo 1980 a 2026")

df       = load_catalog()
metricas = load_metricas()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Titulos analizados",  f"{len(df):,}")
col2.metric("Plataformas",         df['platform'].nunique())
col3.metric("Generos distintos",   df['primary_genre'].nunique())
col4.metric("Calificacion IMDb prom.", f"{df['imdb_rating'].mean():.2f}")
col5.metric("Titulos exitosos",    f"{df['is_hit'].mean():.1%}")

st.divider()

st.subheader("Horas vistas por plataforma y genero")
df_tree = (
    df.groupby(['platform', 'primary_genre'])['hours_watched_million']
    .sum().reset_index()
    .rename(columns={'hours_watched_million': 'horas_vistas'})
)
fig = px.treemap(
    df_tree,
    path=['platform', 'primary_genre'],
    values='horas_vistas',
    title='Horas vistas acumuladas (millones) — tamano proporcional a la audiencia',
    color='horas_vistas',
    color_continuous_scale='Blues',
)
fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)
st.caption("Cada rectangulo representa una combinacion plataforma-genero. Los mas grandes concentran mas audiencia.")

st.divider()

st.subheader("Precision de los modelos de prediccion")
filas = []
for k, v in metricas.items():
    fila = {
        'Modelo':             v['modelo'],
        'Que predice':        v['target'],
        'Exactitud':          v.get('accuracy', '-'),
        'F1':                 v.get('f1_weighted', '-'),
        'Discriminacion ROC': v.get('roc_auc', '-'),
    }
    filas.append(fila)
st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
st.caption(
    "Exactitud: porcentaje de predicciones correctas. "
    "F1: balance entre precision y cobertura. "
    "ROC: capacidad de separar exitosos de no exitosos (1.0 = perfecto)."
)

st.markdown("---")
st.info("Usa el menu lateral para explorar el analisis completo.")
