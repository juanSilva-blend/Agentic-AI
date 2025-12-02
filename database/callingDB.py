import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///sales.db")

# Insert a simple example row
example_row = pd.DataFrame([{
    "vendedor": "Felipe Garzon",
    "sede": "Medellín",
    "producto": "Tablet",
    "cantidad": 5,
    "precio": 1500,
    "fecha": "2025-12-02"
}])
example_row.to_sql("sales", engine, if_exists="append", index=False)
print("Example row inserted!")

# Query the data
df = pd.read_sql_query("SELECT * FROM sales WHERE vendedor = 'Felipe Garzon'", engine)
print(df)

# Example update - change the price for our inserted row
with engine.connect() as conn:
    conn.execute(text("UPDATE sales SET precio = 1800 WHERE vendedor = 'Felipe Garzon' AND producto = 'Tablet'"))
    conn.commit()
print("Example row updated!")

# Query to verify update
df = pd.read_sql_query("SELECT * FROM sales WHERE vendedor = 'Felipe Garzon'", engine)
print(df)

# Example delete - remove the inserted row
with engine.connect() as conn:
    conn.execute(text("DELETE FROM sales WHERE vendedor = 'Felipe Garzon' AND producto = 'Tablet'"))
    conn.commit()
print("Example row deleted!")

# Query to verify deletion
df = pd.read_sql_query("SELECT * FROM sales WHERE vendedor = 'Felipe Garzon'", engine)
print(df)