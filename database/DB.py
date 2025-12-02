import pandas as pd
from sqlalchemy import create_engine

# Nombre del archivo CSV
CSV_FILE = "sales.csv"

DB_FILE = "sales.db"

df = pd.read_csv(CSV_FILE)

# 2. Crear engine de SQLite
engine = create_engine(f"sqlite:///{DB_FILE}")

# 3. Guardar el dataframe como tabla SQL
df.to_sql("sales", engine, if_exists="replace", index=False)

print("Base de datos creada a partir del CSV correctamente.")
