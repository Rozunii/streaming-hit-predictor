import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from dashboard.utils import load_models, load_scalers, load_encoders, load_features_config, load_catalog
from src.feature_engineering import agregar_features
from src.preprocessing import COLUMNAS_CATEGORICAS

AZULES_3 = ['#93c5fd', '#2563eb', '#1e3a5f']

st.set_page_config(page_title="Predice la Calidad", layout="wide")
st.title("Predictor de Calidad Percibida")
st.caption(
    "Estima como calificaria el publico este titulo: Baja, Media o Alta calificacion IMDb."
)

df_ref  = load_catalog()
modelos = load_models()
scalers = load_scalers()
encoders = load_encoders()
FEATURES_NN = load_features_config()['FEATURES_NN']

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
    presupuesto   = st.number_input("Presupuesto (millones USD)", 0.0, 500.0, 0.0, step=1.0)
with col3:
    awards_won     = st.number_input("Premios ganados", 0, 200, 0, step=1)
    tamanio_elenco = st.slider("Actores en el elenco", 0, 50, 8)
    imdb_votes     = st.number_input("Votos IMDb estimados", 0, 3000000, 0, step=1000)
    rt_score       = st.slider("Puntaje Rotten Tomatoes (0-100)", 0, 100, 65)

date_added = st.date_input("Fecha de incorporacion a la plataforma",
                           value=pd.Timestamp.today().date())

if st.button("Predecir calidad", type="primary"):
    row = {
        'type': tipo, 'platform': platform, 'primary_genre': primary_genre, 'rating': rating,
        'release_year': release_year,
        'budget_million_usd': presupuesto if presupuesto > 0 else np.nan,
        'awards_won': awards_won,
        'cast': ','.join(['actor'] * tamanio_elenco),
        'genres': primary_genre,
        'imdb_votes': imdb_votes,
        'date_added': pd.Timestamp(date_added),
        'duration_minutes': 100.0 if tipo == 'Movie' else np.nan,
        'num_episodes': 10.0 if tipo == 'TV Show' else np.nan,
        'imdb_rating': 7.0,
        'rotten_tomatoes_score': float(rt_score),
        'hours_watched_million': 0.0,
    }
    df_row = pd.DataFrame([row])
    try:
        df_row = agregar_features(df_row)
        for col in COLUMNAS_CATEGORICAS:
            le  = encoders[col]
            val = df_row[col].iloc[0]
            df_row[col + '_cod'] = le.transform([val])[0] if val in le.classes_ else 0

        X_nn     = df_row[FEATURES_NN].fillna(0)
        X_scaled = scalers['nn'].transform(X_nn)
        proba    = modelos['mlp'].predict(X_scaled, verbose=0)[0]
        clases   = ['Baja', 'Media', 'Alta']
        pred_idx = int(proba.argmax())

        st.divider()
        st.subheader("Calidad estimada por el modelo")

        fig = px.bar(
            x=clases,
            y=proba,
            color=clases,
            color_discrete_map={
                'Baja':  AZULES_3[0],
                'Media': AZULES_3[1],
                'Alta':  AZULES_3[2],
            },
            labels={'x': 'Nivel de calidad', 'y': 'Probabilidad estimada'},
        )
        fig.update_layout(
            showlegend=False,
            yaxis_tickformat='.0%',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)

        prob_pct = f"{proba[pred_idx]:.0%}"
        st.success(
            f"El modelo estima que este titulo tendra una calificacion IMDb **{clases[pred_idx]}** "
            f"con una confianza del {prob_pct}."
        )
        st.caption(
            "Bajo = IMDb < 6.1  |  Medio = 6.1 a 7.6  |  Alto = IMDb > 7.6. "
            "La prediccion se basa en caracteristicas del titulo, no en la calificacion real."
        )

    except Exception as e:
        st.error(f"Error al calcular: {e}")
        import traceback; st.code(traceback.format_exc())
