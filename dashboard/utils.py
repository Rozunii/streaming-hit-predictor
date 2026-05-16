import streamlit as st
import joblib
import json
import pandas as pd
import numpy as np
import sys
import os

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from src.preprocessing import COLUMNAS_NUMERICAS

@st.cache_resource
def load_models():
    base = os.path.join(_BASE, 'models')
    return {
        'dt':     joblib.load(os.path.join(base, 'decision_tree.joblib')),
        'svm':    joblib.load(os.path.join(base, 'svm.joblib')),
        'mlp':    joblib.load(os.path.join(base, 'mlp.joblib')),
        'kmeans': joblib.load(os.path.join(base, 'kmeans.joblib')),
    }

@st.cache_resource
def load_scalers():
    base = os.path.join(_BASE, 'models')
    return {
        'clf': joblib.load(os.path.join(base, 'scaler_clf.joblib')),
        'nn':  joblib.load(os.path.join(base, 'scaler_nn.joblib')),
        'km':  joblib.load(os.path.join(base, 'scaler_km.joblib')),
    }

@st.cache_resource
def load_encoders():
    return joblib.load(os.path.join(_BASE, 'models', 'encoders.joblib'))

@st.cache_resource
def load_features_config():
    path = os.path.join(_BASE, 'models', 'features_config.json')
    with open(path) as f:
        return json.load(f)

@st.cache_data
def load_catalog():
    path = os.path.join(_BASE, 'data', 'processed', 'catalogo_procesado.csv')
    return pd.read_csv(path)

@st.cache_data
def load_cluster_labels():
    path = os.path.join(_BASE, 'data', 'processed', 'cluster_labels.csv')
    return pd.read_csv(path, index_col=0)

@st.cache_data
def load_metricas():
    path = os.path.join(_BASE, 'models', 'metricas.json')
    with open(path) as f:
        return json.load(f)

NOMBRES_CLUSTERS = {
    0: 'Blockbuster Costoso',
    1: 'Nicho Subestimado',
    2: 'Joya de Critica',
    3: 'Contenido Promedio',
}

FEATURES_KM = [
    'imdb_rating', 'rotten_tomatoes_score', 'votos_log', 'presupuesto_log',
    'awards_won', 'hours_watched_million', 'duracion_total', 'antiguedad',
]
