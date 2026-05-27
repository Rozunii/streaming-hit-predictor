import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from dashboard.utils import load_catalog

AZUL_OSCURO = '#1e3a5f'
AZUL_CLARO  = '#60a5fa'
AZUL_BASE   = '#2563eb'
AZULES_N    = ['#1e3a5f', '#1d4ed8', '#2563eb', '#3b82f6',
               '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff', '#f0f9ff']

st.set_page_config(page_title="Comparar Plataformas", layout="wide")
st.title("Comparar Plataformas")
st.caption("Evalua el desempeno de cada plataforma en calidad, exito comercial y premios.")

df = load_catalog()
plataformas = sorted(df['platform'].unique())

metricas_plat = df.groupby('platform').agg(
    Titulos=('show_id', 'count'),
    IMDb_prom=('imdb_rating', 'mean'),
    RT_prom=('rotten_tomatoes_score', 'mean'),
    Horas_totales_M=('hours_watched_million', 'sum'),
    Pct_exitosos=('is_hit', 'mean'),
    Premios_prom=('awards_won', 'mean'),
).round(2).reset_index()

metricas_pres = metricas_plat.copy()
metricas_pres['Pct_exitosos'] = (metricas_pres['Pct_exitosos'] * 100).round(1).astype(str) + '%'
metricas_pres.columns = ['Plataforma', 'Titulos', 'IMDb prom.', 'Rotten Tomatoes prom.',
                          'Horas totales (M)', '% Exitosos', 'Premios prom.']

st.subheader("Resumen por plataforma")
st.dataframe(metricas_pres, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Comparar dos plataformas")
col1, col2 = st.columns(2)
plat_a = col1.selectbox("Plataforma A", plataformas, index=0)
plat_b = col2.selectbox("Plataforma B", plataformas, index=1)

DIMENSIONES = ['IMDb_prom', 'RT_prom', 'Pct_exitosos', 'Premios_prom']
LABELS       = ['Calificacion IMDb', 'Rotten Tomatoes', '% Titulos exitosos', 'Premios promedio']

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
for plat, color in [(plat_a, AZUL_OSCURO), (plat_b, AZUL_CLARO)]:
    vals = get_radar(plat)
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=LABELS + [LABELS[0]],
        fill='toself',
        name=plat,
        line_color=color,
        fillcolor=color.replace(')', ', 0.15)').replace('rgb', 'rgba') if color.startswith('rgb') else color,
        opacity=0.85,
    ))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    showlegend=True,
    title='Comparacion en cuatro dimensiones (valores normalizados 0-1)',
    paper_bgcolor='rgba(0,0,0,0)',
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Los valores se normalizan entre 0 y 1 para hacer comparables dimensiones con escalas distintas.")

st.divider()

st.subheader("Titulos exitosos por genero y plataforma")
genero_plat = df.groupby(['platform', 'primary_genre'])['is_hit'].mean().reset_index()
genero_plat.columns = ['Plataforma', 'Genero', 'Pct_exitosos']
top_generos = df['primary_genre'].value_counts().head(8).index.tolist()
genero_plat = genero_plat[genero_plat['Genero'].isin(top_generos)]

fig2 = px.bar(
    genero_plat, x='Plataforma', y='Pct_exitosos', color='Genero',
    barmode='group',
    color_discrete_sequence=AZULES_N[:8],
    labels={'Pct_exitosos': '% Titulos exitosos', 'Plataforma': 'Plataforma'},
)
fig2.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    yaxis_tickformat='.0%',
)
st.plotly_chart(fig2, use_container_width=True)
st.caption("Porcentaje de titulos que superaron la mediana de horas vistas, por plataforma y genero principal.")
