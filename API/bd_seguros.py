
import pandas as pd

from app_seguros import app, db

df = pd.read_csv("../data/df_limpio.csv")

with app.app_context():
    db.drop_all()
    db.create_all()         # crea la tabla a partir de la clase Prestamo
    df.to_sql("prestamos", db.engine, if_exists="append", index=False)

print(f"Base de datos creada con {len(df)} préstamos")
