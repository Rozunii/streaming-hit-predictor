import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from dashboard.utils import load_cluster_labels, NOMBRES_CLUSTERS

st.set_page_config(page_title="Clusters de Contenido", layout="wide")
st.title("Segmentacion de Contenido (K-Means)")
st.caption("Los 15,000 titulos agrupados en 4 perfiles de contenido mediante clustering no supervisado.")

df_clusters = load_cluster_labels()
df_clusters['cluster_nombre'] = df_clusters['cluster'].map(NOMBRES_CLUSTERS)

# Heatmap de figura guardada
import os
st.subheader("Perfil de clusters (heatmap)")
fig_path = os.path.join(os.path.dirname(__file__), '..', '..', 'reports', 'figures', '19_heatmap_clusters.png')
if os.path.exists(fig_path):
    st.image(fig_path, use_container_width=True)

st.divider()

# Distribucion
st.subheader("Distribucion de titulos por cluster")
dist = df_clusters['cluster_nombre'].value_counts().reset_index()
dist.columns = ['Cluster', 'Titulos']
fig = px.bar(dist, x='Cluster', y='Titulos', color='Cluster')
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Tabla filtrable
st.subheader("Explorar titulos por cluster")
cluster_sel = st.selectbox("Selecciona un cluster", list(NOMBRES_CLUSTERS.values()))
df_sel = df_clusters[df_clusters['cluster_nombre'] == cluster_sel]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Titulos", len(df_sel))
col2.metric("IMDb promedio", f"{df_sel['imdb_rating'].mean():.2f}")
col3.metric("Horas vistas (M)", f"{df_sel['hours_watched_million'].mean():.1f}")
col4.metric("RT Score promedio", f"{df_sel['rotten_tomatoes_score'].mean():.1f}")

st.dataframe(
    df_sel[['imdb_rating', 'rotten_tomatoes_score', 'hours_watched_million', 'awards_won', 'antiguedad']].round(2),
    use_container_width=True,
)

# PCA 3D imagen
st.divider()
st.subheader("Proyeccion PCA-3D de clusters")
fig3d_path = os.path.join(os.path.dirname(__file__), '..', '..', 'reports', 'figures', '20_pca3d_clusters.png')
if os.path.exists(fig3d_path):
    st.image(fig3d_path, use_container_width=True)
