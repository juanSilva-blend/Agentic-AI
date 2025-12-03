import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///sales.db")

# ============================================================
# Query 1: Top 5 productos más vendidos en Medellín
# ============================================================
print("=" * 60)
print("Query 1: Top 5 productos más vendidos en Medellín")
print("=" * 60)

df_top5 = pd.read_sql_query("""
    SELECT producto, SUM(cantidad) AS total_vendido 
    FROM sales 
    WHERE sede='Medellín' 
    GROUP BY producto 
    ORDER BY total_vendido DESC 
    LIMIT 5
""", engine)
print(df_top5)

# ============================================================
# Query 2: Ventas por vendedor
# ============================================================
print("\n" + "=" * 60)
print("Query 2: Ventas por vendedor")
print("=" * 60)

df_ventas_vendedor = pd.read_sql_query("""
    SELECT vendedor, SUM(cantidad * precio) AS total_ventas 
    FROM sales 
    GROUP BY vendedor
""", engine)
print(df_ventas_vendedor)

# ============================================================
# Query 3: Vendedor con más ventas en Bogotá
# ============================================================
print("\n" + "=" * 60)
print("Query 3: Vendedor con más ventas en Bogotá")
print("=" * 60)

df_top_vendedor_bogota = pd.read_sql_query("""
    SELECT vendedor, SUM(cantidad * precio) AS total_ventas 
    FROM sales 
    WHERE sede='Bogotá' 
    GROUP BY vendedor 
    ORDER BY total_ventas DESC 
    LIMIT 1
""", engine)
print(df_top_vendedor_bogota)