import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dashboard.utils import load_catalog, load_metricas

st.set_page_config(
    page_title="Streaming Hit Predictor",
    page_icon=None,
    layout="wide",
)

st.title("Streaming Hit Predictor")
st.caption("Analisis de 15,000 titulos de 10 plataformas de streaming (1980-2026)")

df = load_catalog()
metricas = load_metricas()

# KPIs
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Titulos", f"{len(df):,}")
col2.metric("Hits", f"{df['is_hit'].mean():.1%}")
col3.metric("Plataformas", df['platform'].nunique())
col4.metric("Generos", df['primary_genre'].nunique())
col5.metric("IMDb promedio", f"{df['imdb_rating'].mean():.2f}")

st.divider()

# Treemap hero
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
    title='Horas vistas acumuladas (millones)',
    color='horas_vistas',
    color_continuous_scale='Blues',
)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# Tabla de metricas
st.divider()
st.subheader("Metricas de modelos")
import pandas as pd
filas = []
for k, v in metricas.items():
    fila = {'Modelo': v['modelo'], 'Target': v['target']}
    fila['Accuracy'] = v.get('accuracy', '-')
    fila['F1'] = v.get('f1_weighted', '-')
    fila['ROC-AUC'] = v.get('roc_auc', '-')
    filas.append(fila)
st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

st.caption("Navega por las paginas del sidebar para explorar el analisis completo.")
