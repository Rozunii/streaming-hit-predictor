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

AZUL_BARRA  = '#2563eb'
COLOR_BAJO  = '#dbeafe'
COLOR_ALTO  = '#1e3a5f'

st.set_page_config(page_title="Predice el Exito", layout="wide")
st.title("Predictor de Exito Comercial")
st.caption(
    "Ingresa las caracteristicas de un titulo para estimar si alcanzara un alto nivel de audiencia."
)

df_ref  = load_catalog()
modelos = load_models()
scalers = load_scalers()
encoders = load_encoders()
FEATURES_CLF = load_features_config()['FEATURES_CLF']

st.subheader("Caracteristicas del titulo")
col1, col2, col3 = st.columns(3)
with col1:
    platform      = st.selectbox("Plataforma", sorted(df_ref['platform'].unique()))
    primary_genre = st.selectbox("Genero principal", sorted(df_ref['primary_genre'].dropna().unique()))
    tipo          = st.radio("Tipo", ['Movie', 'TV Show'],
                             format_func=lambda x: 'Pelicula' if x == 'Movie' else 'Serie')
with col2:
    rating        = st.selectbox("Clasificacion de audiencia", sorted(df_ref['rating'].dropna().unique()))
    release_year  = st.slider("Ano de lanzamiento", 1980, 2026, 2022)
    presupuesto   = st.number_input("Presupuesto (millones USD — 0 si desconocido)", 0.0, 500.0, 0.0, step=1.0)
with col3:
    awards_won     = st.number_input("Premios ganados", 0, 200, 0, step=1)
    tamanio_elenco = st.slider("Actores en el elenco", 0, 50, 8)
    imdb_votes     = st.number_input("Votos IMDb estimados (0 si desconocido)", 0, 3000000, 0, step=1000)

col4, col5 = st.columns(2)
with col4:
    if tipo == 'Movie':
        duration_minutes = st.slider("Duracion (minutos)", 60, 240, 100)
        num_episodes = None
    else:
        num_episodes = st.slider("Numero de episodios", 1, 200, 10)
        duration_minutes = None
with col5:
    rotten_tomatoes_score = st.slider("Puntaje Rotten Tomatoes (0-100)", 0, 100, 65)
    date_added = st.date_input("Fecha de incorporacion a la plataforma",
                               value=pd.Timestamp.today().date())

if st.button("Predecir probabilidad de exito", type="primary"):
    row = {
        'type': tipo, 'platform': platform, 'primary_genre': primary_genre, 'rating': rating,
        'release_year': release_year,
        'budget_million_usd': presupuesto if presupuesto > 0 else np.nan,
        'awards_won': awards_won,
        'cast': ','.join(['actor'] * tamanio_elenco),
        'genres': primary_genre,
        'imdb_votes': imdb_votes,
        'date_added': pd.Timestamp(date_added),
        'duration_minutes': float(duration_minutes) if duration_minutes else np.nan,
        'num_episodes': float(num_episodes) if num_episodes else np.nan,
        'imdb_rating': 7.0,
        'rotten_tomatoes_score': float(rotten_tomatoes_score),
        'hours_watched_million': 0.0,
    }
    df_row = pd.DataFrame([row])

    try:
        df_row = agregar_features(df_row)
        for col in COLUMNAS_CATEGORICAS:
            le  = encoders[col]
            val = df_row[col].iloc[0]
            df_row[col + '_cod'] = le.transform([val])[0] if val in le.classes_ else 0

        X_clf    = df_row[FEATURES_CLF].fillna(0)
        X_scaled = scalers['clf'].transform(X_clf)
        prob_dt  = modelos['dt'].predict_proba(X_scaled)[0][1]
        prob_svm = modelos['svm'].predict_proba(X_scaled)[0][1]

        st.divider()
        st.subheader("Probabilidad de ser un titulo exitoso")
        c1, c2 = st.columns(2)
        for col_ui, nombre, prob in [(c1, 'Modelo 1', prob_dt), (c2, 'Modelo 2', prob_svm)]:
            with col_ui:
                etiq = 'EXITOSO' if prob >= 0.5 else 'No alcanza el umbral'
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(prob * 100, 1),
                    number={'suffix': '%'},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': AZUL_BARRA},
                        'steps': [
                            {'range': [0,  50], 'color': COLOR_BAJO},
                            {'range': [50, 100], 'color': COLOR_ALTO},
                        ],
                        'threshold': {
                            'line': {'color': '#1e3a5f', 'width': 3},
                            'value': 50,
                        },
                    },
                    title={'text': f'{nombre}: {etiq}'},
                ))
                fig.update_layout(height=260, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

        acuerdo = (prob_dt >= 0.5) == (prob_svm >= 0.5)
        if acuerdo:
            if prob_dt >= 0.5:
                st.success("Ambos modelos coinciden: el titulo tiene alta probabilidad de ser exitoso.")
            else:
                st.warning("Ambos modelos coinciden: el titulo tiene baja probabilidad de superar el umbral de audiencia.")
        else:
            st.info("Los dos modelos dan resultados distintos. Se recomienda analizar el contexto antes de decidir.")

        st.divider()
        st.subheader("Perfil de contenido similar")
        X_km_raw    = df_row[FEATURES_KM].fillna(0)
        X_km_scaled = scalers['km'].transform(X_km_raw)
        cluster     = modelos['kmeans'].predict(X_km_scaled)[0]
        nombre_cluster = NOMBRES_CLUSTERS.get(int(cluster), f'Grupo {cluster}')
        st.info(
            f"Este titulo es similar a los del **{nombre_cluster}**. "
            "Puedes ver las caracteristicas de ese grupo en la pagina 'Perfiles de Contenido'."
        )

    except Exception as e:
        st.error(f"Error al calcular: {e}")
        import traceback; st.code(traceback.format_exc())
