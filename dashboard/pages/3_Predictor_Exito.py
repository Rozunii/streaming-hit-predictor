import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from dashboard.utils import (
    load_models, load_scalers, load_encoders, load_features_config,
    load_catalog, NOMBRES_CLUSTERS, FEATURES_KM
)
from src.feature_engineering import agregar_features
from src.preprocessing import COLUMNAS_CATEGORICAS

st.set_page_config(page_title="Predictor de Exito", layout="wide")
st.title("Predictor de Exito Comercial")
st.caption("Ingresa las caracteristicas de un titulo para predecir si sera un Hit (is_hit)")

df_ref = load_catalog()
modelos = load_models()
scalers = load_scalers()
encoders = load_encoders()
FEATURES_CLF = load_features_config()['FEATURES_CLF']

col1, col2, col3 = st.columns(3)
with col1:
    platform     = st.selectbox("Plataforma", sorted(df_ref['platform'].unique()))
    primary_genre= st.selectbox("Genero principal", sorted(df_ref['primary_genre'].dropna().unique()))
    tipo         = st.radio("Tipo", ['Movie', 'TV Show'])
with col2:
    rating       = st.selectbox("Rating de contenido", sorted(df_ref['rating'].dropna().unique()))
    release_year = st.slider("Anio de lanzamiento", 1980, 2026, 2022)
    presupuesto  = st.number_input("Presupuesto (M USD, 0=desconocido)", 0.0, 500.0, 0.0, step=1.0)
with col3:
    awards_won    = st.number_input("Premios ganados", 0, 200, 0, step=1)
    tamanio_elenco= st.slider("Actores en el elenco", 0, 50, 8)
    imdb_votes    = st.number_input("Votos IMDb estimados (0=desconocido)", 0, 3000000, 0, step=1000)

col4, col5 = st.columns(2)
with col4:
    if tipo == 'Movie':
        duration_minutes = st.slider("Duracion (minutos)", 60, 240, 100)
        num_episodes = None
    else:
        num_episodes = st.slider("Numero de episodios", 1, 200, 10)
        duration_minutes = None
with col5:
    rotten_tomatoes_score = st.slider("Rotten Tomatoes Score", 0, 100, 65)
    date_added = st.date_input("Fecha de incorporacion", value=pd.Timestamp.today().date())

if st.button("Predecir", type="primary"):
    row = {
        'type': tipo, 'platform': platform, 'primary_genre': primary_genre, 'rating': rating,
        'release_year': release_year, 'budget_million_usd': presupuesto if presupuesto > 0 else np.nan,
        'awards_won': awards_won, 'cast': ','.join(['actor'] * tamanio_elenco),
        'genres': primary_genre, 'imdb_votes': imdb_votes,
        'date_added': pd.Timestamp(date_added),
        'duration_minutes': float(duration_minutes) if duration_minutes else np.nan,
        'num_episodes': float(num_episodes) if num_episodes else np.nan,
        'imdb_rating': 7.0, 'rotten_tomatoes_score': float(rotten_tomatoes_score),
        'hours_watched_million': 0.0,
    }
    df_row = pd.DataFrame([row])

    try:
        df_row = agregar_features(df_row)
        for col in COLUMNAS_CATEGORICAS:
            le = encoders[col]
            val = df_row[col].iloc[0]
            df_row[col + '_cod'] = le.transform([val])[0] if val in le.classes_ else 0

        X_clf   = df_row[FEATURES_CLF].fillna(0)
        X_scaled= scalers['clf'].transform(X_clf)
        prob_dt  = modelos['dt'].predict_proba(X_scaled)[0][1]
        prob_svm = modelos['svm'].predict_proba(X_scaled)[0][1]

        st.divider()
        st.subheader("Probabilidad de ser un Hit")
        c1, c2 = st.columns(2)
        for col_ui, nombre, prob in [(c1, 'Arbol de Decision', prob_dt), (c2, 'SVM', prob_svm)]:
            with col_ui:
                color  = 'green' if prob >= 0.5 else 'red'
                etiq   = 'HIT' if prob >= 0.5 else 'No Hit'
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=round(prob * 100, 1),
                    number={'suffix': '%'},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': color},
                           'steps': [{'range': [0, 50], 'color': '#ffcccc'},
                                     {'range': [50, 100], 'color': '#ccffcc'}],
                           'threshold': {'line': {'color': 'black', 'width': 3}, 'value': 50}},
                    title={'text': f'{nombre}: {etiq}'}
                ))
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)

        acuerdo = (prob_dt >= 0.5) == (prob_svm >= 0.5)
        if acuerdo:
            st.success("Ambos modelos concuerdan.")
        else:
            st.warning("Los modelos difieren. Considera el contexto.")

        # Cluster K-Means con datos escalados
        st.subheader("Perfil de cluster (K-Means)")
        X_km_raw = df_row[FEATURES_KM].fillna(0)
        X_km_scaled = scalers['km'].transform(X_km_raw)
        cluster = modelos['kmeans'].predict(X_km_scaled)[0]
        nombre_cluster = NOMBRES_CLUSTERS.get(int(cluster), f'Cluster {cluster}')
        st.info(f"Cluster asignado: **{nombre_cluster}** (Cluster {cluster})")

    except Exception as e:
        st.error(f"Error al predecir: {e}")
        import traceback; st.code(traceback.format_exc())
