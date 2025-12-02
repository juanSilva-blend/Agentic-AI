import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///sales.db")
df = pd.read_sql_query("SELECT * FROM sales LIMIT 5", engine)
print(df)