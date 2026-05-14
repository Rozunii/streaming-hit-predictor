import numpy as np
import pandas as pd


def agregar_features(df):
    """Crea columnas nuevas a partir de las existentes para mejorar los modelos."""
    df = df.copy()

    # 1 si es pelicula, 0 si es serie
    df['es_pelicula'] = (df['type'] == 'Movie').astype(int)

    # Cuantos generos tiene el titulo
    df['cantidad_generos'] = df['genres'].str.split(',').str.len().fillna(1)

    # Cuantos actores tiene en el elenco
    df['tamanio_elenco'] = df['cast'].str.split(',').str.len().fillna(0)

    # Cuantos años tiene desde que se lanzo
    df['antiguedad'] = 2026 - df['release_year']

    # 1 si se lanzo en 2020 o despues
    df['es_reciente'] = (df['release_year'] >= 2020).astype(int)

    # Mes en que fue agregado a la plataforma (puede capturar estacionalidad)
    # date_added ya debe estar en formato datetime antes de llamar esta funcion
    df['mes_agregado'] = df['date_added'].dt.month.fillna(6).astype(int)

    # Dias transcurridos desde que se agrego a la plataforma
    # Se usa clip(0) para que fechas futuras no den valores negativos
    hoy = pd.Timestamp('2026-05-13')
    df['dias_en_plataforma'] = (hoy - df['date_added']).dt.days.fillna(0).clip(lower=0).astype(int)

    # Los votos de IMDb tienen valores muy grandes, usar log los comprime
    df['votos_log'] = np.log1p(df['imdb_votes'].fillna(0))

    # Igual para el presupuesto, las series sin datos quedan en 0
    df['presupuesto_log'] = np.log1p(df['budget_million_usd'].fillna(0))

    # 1 si tiene presupuesto reportado, 0 si no
    df['tiene_presupuesto'] = df['budget_million_usd'].notna().astype(int)

    # Duracion en minutos: para peliculas se usa el dato directo,
    # para series se estima como episodios x 45 minutos
    df['duracion_total'] = np.where(
        df['es_pelicula'] == 1,
        df['duration_minutes'].fillna(df['duration_minutes'].median()),
        df['num_episodes'].fillna(10) * 45
    )

    return df


def crear_targets(df):
    """
    Crea las dos columnas que usaremos como objetivo (target):
    - is_hit: 1 si las horas vistas superan la mediana (exito comercial)
    - imdb_clase: Bajo / Medio / Alto segun el rating de IMDb
    """
    df = df.copy()

    mediana_horas = df['hours_watched_million'].median()
    df['is_hit'] = (df['hours_watched_million'] >= mediana_horas).astype(int)

    # Dividimos el rating de IMDb en tres categorias usando los percentiles reales
    # del dataset (p25=6.1, p75=7.6) para que las clases queden balanceadas
    df['imdb_clase'] = pd.cut(
        df['imdb_rating'],
        bins=[0, 6.1, 7.6, 10],
        labels=['Bajo', 'Medio', 'Alto']
    )

    return df, mediana_horas
