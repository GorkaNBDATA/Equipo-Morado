
import unicodedata
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://clase:clase123@localhost:3306/creditos"
from pathlib import Path

DATA_DIR = Path("../datos")
LIMPIO_FILE = DATA_DIR / "df_limpio.csv"
PREDICCIONES_FILE = DATA_DIR / "df_prediccion_prima.csv"

TABLE_NAME = "prestamos"


def normalizar_nombre(nombre):
    return (
        unicodedata.normalize("NFKD", str(nombre))
        .encode("ascii", "ignore")
        .decode("ascii")
        .strip()
        .replace(" ", "_")
    )


def leer_y_unir_datos():
    df_limpio = pd.read_csv(LIMPIO_FILE)
    df_modelo = pd.read_csv(PREDICCIONES_FILE)

    predicciones = df_modelo[
        ["ID", "prob_impago", "prediccion", "predicciones_Prima"]
    ]

    df_api = df_limpio.merge(
        predicciones,
        on="ID",
        how="inner"
    )

    df_api.columns = [
        normalizar_nombre(c)
        for c in df_api.columns
    ]

    return df_api


def main():
    engine = create_engine(DATABASE_URL)

    df_api = leer_y_unir_datos()

    print(f"Cargando {len(df_api)} préstamos...")

    df_api.to_sql(
        TABLE_NAME,
        engine,
        if_exists="replace",
        index=False
    )

    print("Carga de datos completada.")


if __name__ == "__main__":
    main()

