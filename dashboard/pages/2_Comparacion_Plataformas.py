import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from dashboard.utils import load_catalog

st.set_page_config(page_title="Comparacion Plataformas", layout="wide")
st.title("Comparacion de Plataformas")

df = load_catalog()
plataformas = sorted(df['platform'].unique())

# Metricas por plataforma
metricas_plat = df.groupby('platform').agg(
    titulos=('show_id', 'count'),
    imdb_promedio=('imdb_rating', 'mean'),
    rt_promedio=('rotten_tomatoes_score', 'mean'),
    horas_totales=('hours_watched_million', 'sum'),
    pct_hits=('is_hit', 'mean'),
    awards_promedio=('awards_won', 'mean'),
).round(2).reset_index()

st.subheader("Resumen por plataforma")
st.dataframe(metricas_plat, use_container_width=True, hide_index=True)

st.divider()

# Radar comparativo
st.subheader("Comparacion radar entre dos plataformas")
col1, col2 = st.columns(2)
plat_a = col1.selectbox("Plataforma A", plataformas, index=0)
plat_b = col2.selectbox("Plataforma B", plataformas, index=1)

DIMENSIONES = ['imdb_promedio', 'rt_promedio', 'pct_hits', 'awards_promedio']
LABELS = ['IMDb', 'Rotten Tomatoes', '% Hits', 'Premios (media)']

def normalizar(serie):
    mn, mx = serie.min(), serie.max()
    return (serie - mn) / (mx - mn + 1e-9)

metricas_norm = metricas_plat.copy()
for col in DIMENSIONES:
    metricas_norm[col] = normalizar(metricas_plat[col])

def get_radar(plat):
    row = metricas_norm[metricas_norm['platform'] == plat]
    if row.empty:
        return [0] * len(DIMENSIONES)
    return row[DIMENSIONES].values[0].tolist()

fig = go.Figure()
for plat, color in [(plat_a, 'steelblue'), (plat_b, 'darkorange')]:
    vals = get_radar(plat)
    fig.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=LABELS + [LABELS[0]],
                                  fill='toself', name=plat, line_color=color))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                  showlegend=True, title="Radar comparativo (normalizado)")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Mix de generos por plataforma
st.subheader("Mix de generos por plataforma")
genero_plat = df.groupby(['platform', 'primary_genre']).size().reset_index(name='conteo')
fig = px.bar(genero_plat, x='platform', y='conteo', color='primary_genre',
             barmode='stack', labels={'conteo': 'Titulos', 'platform': 'Plataforma'})
st.plotly_chart(fig, use_container_width=True)
