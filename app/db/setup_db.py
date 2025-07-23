import pandas as pd
import sqlite3
import os
from app.core.logger import logging

try:
    logging.info("Starting database setup...")

    ad_sales_path = "data/Product-Level Ad Sales and Metrics (mapped).xlsx"
    total_sales_path = "data/Product-Level Total Sales and Metrics (mapped).xlsx"
    eligibility_path = "data/Product-Level Eligibility Table (mapped).xlsx"
    db_path = "app/db/ai_data_agent.db"


    for file in [ad_sales_path, total_sales_path, eligibility_path]:
        if not os.path.exists(file):
            logging.error(f"Missing input file: {file}")
            raise FileNotFoundError(f"{file} not found")

    logging.info("Reading Excel files...")
    ad_sales = pd.read_excel(ad_sales_path)
    total_sales = pd.read_excel(total_sales_path)
    eligibility = pd.read_excel(eligibility_path)

    logging.info(f"Connecting to database at {db_path}")
    conn = sqlite3.connect(db_path)

    ad_sales.to_sql("ad_sales", conn, if_exists="replace", index=False)
    logging.info("Loaded 'ad_sales' table.")

    total_sales.to_sql("total_sales", conn, if_exists="replace", index=False)
    logging.info("Loaded 'total_sales' table.")

    eligibility.to_sql("eligibility", conn, if_exists="replace", index=False)
    logging.info("Loaded 'eligibility' table.")

    conn.close()
    logging.info("Database setup completed successfully.")

except Exception as e:
    logging.exception("Error during database setup")
