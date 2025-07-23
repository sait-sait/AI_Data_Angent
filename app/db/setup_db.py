import pandas as pd
import sqlite3

# Load Excel files
ad_sales = pd.read_excel("data/Product-Level Ad Sales and Metrics (mapped).xlsx")
total_sales = pd.read_excel("data/Product-Level Total Sales and Metrics (mapped).xlsx")
eligibility = pd.read_excel("data/Product-Level Eligibility Table (mapped).xlsx")

# Create SQLite database
conn = sqlite3.connect("app/db/ai_data_agent.db")
ad_sales.to_sql("ad_sales", conn, if_exists="replace", index=False)
total_sales.to_sql("total_sales", conn, if_exists="replace", index=False)
eligibility.to_sql("eligibility", conn, if_exists="replace", index=False)
conn.close()
print("Database created successfully.")
