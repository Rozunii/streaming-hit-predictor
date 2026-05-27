import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from dashboard.utils import load_catalog

AZUL     = '#2563eb'
AZULES_N = ['#1e3a5f', '#1d4ed8', '#2563eb', '#3b82f6',
            '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff', '#f0f9ff']

st.set_page_config(page_title="Analisis General", layout="wide")
st.title("Analisis General del Catalogo")

df = load_catalog()

st.sidebar.header("Filtros")
plataformas = st.sidebar.multiselect(
    "Plataforma",
    sorted(df['platform'].unique()),
    default=sorted(df['platform'].unique()),
)
tipo = st.sidebar.multiselect(
    "Tipo de contenido",
    df['type'].unique().tolist(),
    default=df['type'].unique().tolist(),
)

mask = df['platform'].isin(plataformas) & df['type'].isin(tipo)
df_f = df[mask]
st.caption(f"Mostrando {len(df_f):,} de {len(df):,} titulos")

# ── Horas vistas y distribucion ──────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribucion de horas vistas")
    fig = px.histogram(
        df_f, x='hours_watched_million', nbins=50,
        color_discrete_sequence=[AZUL],
        labels={'hours_watched_million': 'Horas vistas (millones)', 'count': 'Titulos'},
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.caption("La mayoria de los titulos concentra pocas horas; unos pocos generan una audiencia muy alta.")

with col2:
    st.subheader("Calificacion IMDb vs Horas vistas")
    fig = px.scatter(
        df_f.sample(min(2000, len(df_f))),
        x='imdb_rating', y='hours_watched_million',
        opacity=0.4,
        color_discrete_sequence=[AZUL],
        labels={'imdb_rating': 'Calificacion IMDb', 'hours_watched_million': 'Horas vistas (M)'},
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Una calificacion alta no garantiza mas horas vistas. Hay titulos populares con calificacion media.")

st.divider()

# ── Horas por plataforma ─────────────────────────────────────────────
st.subheader("Horas vistas por plataforma")
plats_orden = df_f.groupby('platform')['hours_watched_million'].median().sort_values(ascending=False).index.tolist()
n = len(plats_orden)
colores = AZULES_N[:n] if n <= len(AZULES_N) else [AZUL] * n
color_map = {p: c for p, c in zip(plats_orden, colores)}

fig = px.box(
    df_f, x='platform', y='hours_watched_million',
    category_orders={'platform': plats_orden},
    color='platform',
    color_discrete_map=color_map,
    labels={'platform': 'Plataforma', 'hours_watched_million': 'Horas vistas (M)'},
)
fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)
st.caption("Cada caja muestra la distribucion de horas. La linea central es la mediana.")

st.divider()

# ── Lanzamientos por anio ────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Titulos por ano de lanzamiento")
    fig = px.histogram(
        df_f, x='release_year', nbins=40,
        color_discrete_sequence=[AZUL],
        labels={'release_year': 'Ano', 'count': 'Titulos'},
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Generos mas frecuentes")
    top_gen = df_f['primary_genre'].value_counts().head(10).reset_index()
    top_gen.columns = ['Genero', 'Titulos']
    fig = px.bar(
        top_gen, x='Titulos', y='Genero', orientation='h',
        color='Titulos',
        color_continuous_scale='Blues',
        labels={'Titulos': 'Cantidad de titulos'},
    )
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        yaxis=dict(autorange='reversed'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    st.plotly_chart(fig, use_container_width=True)
