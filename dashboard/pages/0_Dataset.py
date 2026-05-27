import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from dashboard.utils import load_catalog

AZUL      = '#2563eb'
AZULES_2  = ['#1e3a5f', '#93c5fd']
AZULES_3  = ['#1e3a5f', '#2563eb', '#93c5fd']

st.set_page_config(page_title="El Catalogo", layout="wide")
st.title("El Catalogo de Streaming")
st.caption("15,000 titulos de 10 plataformas — periodo 1980 a 2026")

df = load_catalog()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Titulos totales",      f"{len(df):,}")
c2.metric("Plataformas",          df['platform'].nunique())
c3.metric("Peliculas",            f"{(df['type']=='Movie').sum():,}")
c4.metric("Series",               f"{(df['type']=='TV Show').sum():,}")
c5.metric("Calificacion IMDb prom.", f"{df['imdb_rating'].mean():.2f}")

st.divider()

st.subheader("¿Que medimos?")
st.markdown(
    "Cada titulo tiene dos variables que usamos como medida de exito:"
)
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Exito comercial** — Horas vistas")
    mediana = df['hours_watched_million'].median()
    hits    = (df['hours_watched_million'] >= mediana).sum()
    no_hits = len(df) - hits
    fig = px.pie(
        values=[hits, no_hits],
        names=['Exitoso', 'No exitoso'],
        color_discrete_sequence=AZULES_2,
        hole=0.55,
    )
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=260,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Un titulo es 'exitoso' si supera {mediana:.0f}M de horas vistas (la mitad superior del catalogo).")

with col2:
    st.markdown("**Calidad percibida** — Calificacion IMDb")
    conteo = df['imdb_clase'].value_counts().reindex(['Bajo', 'Medio', 'Alto'])
    fig2 = px.bar(
        x=conteo.index,
        y=conteo.values,
        color=conteo.index,
        color_discrete_map={'Bajo': AZULES_3[0], 'Medio': AZULES_3[1], 'Alto': AZULES_3[2]},
        labels={'x': 'Categoria', 'y': 'Titulos'},
    )
    fig2.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=260,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Bajo = IMDb < 6.1  |  Medio = 6.1 a 7.6  |  Alto = IMDb > 7.6")

st.divider()

st.subheader("Titulos por plataforma")
resumen = (
    df.groupby('platform')
    .agg(
        Titulos=('show_id', 'count'),
        Peliculas=('type', lambda x: (x == 'Movie').sum()),
        Series=('type', lambda x: (x == 'TV Show').sum()),
        IMDb_prom=('imdb_rating', 'mean'),
        Horas_vistas_M=('hours_watched_million', 'mean'),
        Pct_exitosos=('is_hit', 'mean'),
    )
    .sort_values('Titulos', ascending=False)
    .reset_index()
)
resumen['IMDb_prom']      = resumen['IMDb_prom'].round(2)
resumen['Horas_vistas_M'] = resumen['Horas_vistas_M'].round(1)
resumen['Pct_exitosos']   = (resumen['Pct_exitosos'] * 100).round(1).astype(str) + '%'
resumen.columns = ['Plataforma', 'Titulos', 'Peliculas', 'Series',
                   'IMDb prom.', 'Horas vistas prom. (M)', '% Exitosos']
st.dataframe(resumen, use_container_width=True, hide_index=True)
