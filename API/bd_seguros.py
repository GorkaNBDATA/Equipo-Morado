import unicodedata
import pandas as pd
from app_seguros import app, db

def limpiar_nombre(nombre):
    return unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode().strip().replace(" ", "_")


df_limpio = pd.read_csv("../data/df_limpio.csv")
df_modelo = pd.read_csv("../data/df_prediccion_prima.csv")

predicciones = df_modelo[["ID", "prob_impago", "prediccion", "predicciones_Prima"]]

df_api = df_limpio.merge(predicciones, on="ID", how="inner")
df_api.columns = [limpiar_nombre(c) for c in df_api.columns]

df_api.to_csv("../data/df_api.csv", index=False)

with app.app_context():
    db.drop_all()
    db.create_all()
    df_api.to_sql("prestamos", db.engine, if_exists="append", index=False)

print(f"Proceso completado: {len(df_api)} préstamos")