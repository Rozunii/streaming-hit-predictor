import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split


# Features numericas para los modelos
COLUMNAS_NUMERICAS = [
    'release_year', 'antiguedad', 'duracion_total',
    'votos_log', 'presupuesto_log', 'awards_won',
    'cantidad_generos', 'tamanio_elenco',
    'es_pelicula', 'es_reciente', 'tiene_presupuesto',
    'mes_agregado', 'dias_en_plataforma',
]

# Features categoricas que hay que convertir a numeros
COLUMNAS_CATEGORICAS = ['platform', 'primary_genre', 'rating']


def limpiar_datos(df):
    """Elimina duplicados, convierte fechas y rellena nulos simples."""
    df = df.drop_duplicates(subset=['show_id'])
    df = df.drop_duplicates()

    # Convertir date_added de texto a fecha real
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

    # El director puede ser nulo en series donde hay varios directores
    df['director'] = df['director'].fillna('Sin datos')

    return df.reset_index(drop=True)


def codificar_categoricas(df, columnas):
    """
    Convierte columnas de texto a numeros con LabelEncoder.
    Devuelve el dataframe modificado y los encoders (para usarlos luego en el dashboard).
    """
    df = df.copy()
    encoders = {}

    for col in columnas:
        df[col] = df[col].fillna('Desconocido')
        le = LabelEncoder()
        df[col + '_cod'] = le.fit_transform(df[col])
        encoders[col] = le

    return df, encoders


def preparar_datos(df, target_col, cols_features):
    """
    Recibe el dataframe completo con todas las features ya creadas,
    separa X e y, escala los datos y hace el split 80/20.
    Devuelve X_train, X_test, y_train, y_test y el scaler.
    """
    df_limpio = df[cols_features + [target_col]].dropna()

    X = df_limpio[cols_features]
    y = df_limpio[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Escalamos para que todas las columnas tengan la misma magnitud
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test, scaler
