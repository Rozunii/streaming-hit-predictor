import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from dashboard.utils import load_cluster_labels, NOMBRES_CLUSTERS

AZULES_4 = ['#1e3a5f', '#2563eb', '#60a5fa', '#bfdbfe']

st.set_page_config(page_title="Perfiles de Contenido", layout="wide")
st.title("Perfiles de Contenido")
st.caption(
    "El catalogo tiene cuatro grupos naturales de titulos con caracteristicas similares entre si. "
    "Estos perfiles ayudan a entender que tipo de contenido existe y donde posicionarlo."
)

df_clusters = load_cluster_labels()
df_clusters['cluster_nombre'] = df_clusters['cluster'].map(NOMBRES_CLUSTERS)

# ── Heatmap de perfiles ───────────────────────────────────────────────
st.subheader("Que caracteriza a cada perfil")
fig_path = os.path.join(os.path.dirname(__file__), '..', '..', 'reports', 'figures', '19_heatmap_clusters.png')
if os.path.exists(fig_path):
    st.image(fig_path, use_container_width=True)
    st.caption(
        "Cada fila es un perfil y cada columna es una variable normalizada. "
        "Tonos oscuros = valores altos. Tonos claros = valores bajos."
    )

st.divider()

# ── Distribucion ─────────────────────────────────────────────────────
st.subheader("Cuantos titulos hay en cada perfil")
dist = df_clusters['cluster_nombre'].value_counts().reset_index()
dist.columns = ['Perfil', 'Titulos']
dist = dist.sort_values('Perfil')
color_map = {p: c for p, c in zip(sorted(dist['Perfil'].unique()), AZULES_4)}

fig = px.bar(
    dist, x='Perfil', y='Titulos',
    color='Perfil',
    color_discrete_map=color_map,
    labels={'Titulos': 'Cantidad de titulos'},
)
fig.update_layout(
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Explorar un perfil ───────────────────────────────────────────────
st.subheader("Explorar un perfil en detalle")
cluster_sel = st.selectbox("Selecciona un perfil", list(NOMBRES_CLUSTERS.values()))
df_sel = df_clusters[df_clusters['cluster_nombre'] == cluster_sel]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Titulos en el perfil",    len(df_sel))
col2.metric("Calificacion IMDb prom.", f"{df_sel['imdb_rating'].mean():.2f}")
col3.metric("Horas vistas prom. (M)",  f"{df_sel['hours_watched_million'].mean():.1f}")
col4.metric("Puntaje RT prom.",        f"{df_sel['rotten_tomatoes_score'].mean():.1f}")

st.dataframe(
    df_sel[['imdb_rating', 'rotten_tomatoes_score', 'hours_watched_million',
            'awards_won', 'antiguedad']]
    .rename(columns={
        'imdb_rating':            'IMDb',
        'rotten_tomatoes_score':  'Rotten Tomatoes',
        'hours_watched_million':  'Horas vistas (M)',
        'awards_won':             'Premios',
        'antiguedad':             'Antiguedad (anos)',
    })
    .round(2),
    use_container_width=True,
)
