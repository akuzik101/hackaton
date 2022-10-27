import pandas as pd
import sqlite3 as sql

# Create a connection to the database
conn = sql.connect('cultobjects.db')
df = pd.read_csv('objektusaraksts.csv')
df.to_sql('objects', conn)
conn.close()
