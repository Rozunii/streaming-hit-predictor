import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from dashboard.utils import load_catalog

st.set_page_config(page_title="EDA - Exploracion", layout="wide")
st.title("Exploracion de Datos")

df = load_catalog()

# Filtros sidebar
st.sidebar.header("Filtros")
plataformas = st.sidebar.multiselect("Plataforma", sorted(df['platform'].unique()), default=sorted(df['platform'].unique()))
generos = st.sidebar.multiselect("Genero", sorted(df['primary_genre'].dropna().unique()), default=sorted(df['primary_genre'].dropna().unique()))
decadas = st.sidebar.multiselect("Decada", sorted(df['release_year'].apply(lambda x: (x//10)*10).unique()), default=sorted(df['release_year'].apply(lambda x: (x//10)*10).unique()))
tipo = st.sidebar.multiselect("Tipo", df['type'].unique().tolist(), default=df['type'].unique().tolist())

mask = (
    df['platform'].isin(plataformas) &
    df['primary_genre'].isin(generos) &
    df['release_year'].apply(lambda x: (x//10)*10).isin(decadas) &
    df['type'].isin(tipo)
)
df_f = df[mask]
st.caption(f"Titulos filtrados: {len(df_f):,} de {len(df):,}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Distribucion de horas vistas")
    fig = px.histogram(df_f, x='hours_watched_million', nbins=50,
                       labels={'hours_watched_million': 'Horas vistas (millones)'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("IMDb vs Horas vistas")
    fig = px.scatter(df_f.sample(min(2000, len(df_f))), x='imdb_rating', y='hours_watched_million',
                     color='platform', opacity=0.6, size_max=8,
                     labels={'imdb_rating': 'Rating IMDb', 'hours_watched_million': 'Horas (M)'})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Horas vistas por plataforma")
fig = px.box(df_f, x='platform', y='hours_watched_million',
             labels={'platform': 'Plataforma', 'hours_watched_million': 'Horas (M)'},
             color='platform')
st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Distribucion de lanzamientos")
    fig = px.histogram(df_f, x='release_year', nbins=40, labels={'release_year': 'Anio'})
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Correlacion entre variables numericas")
    cols_corr = ['imdb_rating', 'rotten_tomatoes_score', 'hours_watched_million', 'awards_won', 'votos_log']
    corr = df_f[cols_corr].corr().round(2)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
    st.plotly_chart(fig, use_container_width=True)
