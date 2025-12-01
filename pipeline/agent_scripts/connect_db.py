from pathlib import Path
import duckdb
import pandas as pd

DATA_PATH = Path(__file__).parents[1] / "data_warehouse"

def query_data_warehouse(table_name : str):
    with duckdb.connect(DATA_PATH / "prj_job_advertisements.duckdb") as conn:
        new_data = conn.execute(query=f"""
            SELECT * FROM {table_name};
            """)
        df = new_data.df()
    return str(df.columns)

if __name__ == "__main__":
    warehouse_data = query_data_warehouse("staging.prj_daily_job_ads")
    print(warehouse_data)