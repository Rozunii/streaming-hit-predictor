import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from dashboard.utils import load_catalog

AZUL = '#2563eb'

st.set_page_config(page_title="Como funciona", layout="wide")
st.title("Como preparamos los datos")
st.caption("Pasos aplicados antes de entrenar los modelos de prediccion.")

df = load_catalog()

st.subheader("Origen de los datos")
st.markdown(
    "El catalogo contiene **25 columnas originales** por titulo. "
    "Antes de usarlas en los modelos, se aplicaron tres pasos de preparacion:"
)

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Paso 1 — Limpieza**\n\nSe corrigieron valores faltantes segun el tipo de contenido. "
            "Por ejemplo, las series no tienen duracion en minutos, por lo que ese campo se calculo "
            "multiplicando episodios por tiempo promedio.")
with col2:
    st.info("**Paso 2 — Variables nuevas**\n\nSe crearon 11 variables adicionales a partir de las originales, "
            "como la antiguedad del titulo, el tamano del elenco o una version ajustada de los votos IMDb "
            "para reducir el efecto de valores extremos.")
with col3:
    st.info("**Paso 3 — Estandarizacion**\n\nTodas las variables numericas se llevaron a la misma escala "
            "para que ningun valor grande domine sobre los demas al entrenar los modelos.")

st.divider()

st.subheader("Variables creadas")
features = pd.DataFrame([
    ('Tipo de contenido',    'Pelicula (1) o serie (0)'),
    ('Cantidad de generos',  'Cuantos generos tiene el titulo'),
    ('Tamano del elenco',    'Cuantos actores aparecen en creditos'),
    ('Antiguedad',           'Anos desde el estreno hasta 2026'),
    ('Titulo reciente',      '1 si se estreno en 2020 o despues'),
    ('Mes de incorporacion', 'Mes en que llego a la plataforma'),
    ('Dias en plataforma',   'Dias disponible desde que se incorporo'),
    ('Votos IMDb (ajust.)',  'Votos en escala logaritmica para reducir extremos'),
    ('Presupuesto (ajust.)', 'Presupuesto en escala logaritmica, 0 si no se reporto'),
    ('Tiene presupuesto',    '1 si el presupuesto fue reportado, 0 si no'),
    ('Duracion total',       'Minutos para peliculas; episodios x 45 min para series'),
], columns=['Variable', 'Que representa'])
st.dataframe(features, use_container_width=True, hide_index=True)

st.divider()

st.subheader("La variable mas importante para predecir exito")
if 'votos_log' in df.columns:
    st.markdown(
        "La cantidad de votos en IMDb (en escala ajustada) es el indicador con mayor correlacion "
        "con el exito comercial de un titulo. Los titulos mas vistos tienden a tener muchos mas votos."
    )
    fig = px.histogram(
        df, x='votos_log', nbins=60,
        color_discrete_sequence=[AZUL],
        labels={'votos_log': 'Votos IMDb (escala ajustada)', 'count': 'Titulos'},
    )
    fig.update_layout(
        height=250,
        margin=dict(t=10, b=30, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
