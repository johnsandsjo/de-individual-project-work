import duckdb
import pandas as pd
from pathlib import Path

db_path = Path(__file__).parents[1] / "data_warehouse/prj_job_advertisements.duckdb"
csv_path = Path(__file__).parents[2] / "data/scb_stats.csv"
table_name = "scb_stats"


def move_csv_to_duckdb_sql_with_context(csv_path, db_path, table_name):
    #csv_path: Union[str, Path]
    #db_path: Union[str, Path]

    db_path_str = str(db_path)
    csv_path_str = str(csv_path) 
    df = pd.read_csv(csv_path_str, skiprows=2, encoding='latin1')
    
    with duckdb.connect(database=db_path_str) as con:
        con.register('temp_df', df)
        con.execute(f"CREATE TABLE staging.{table_name} AS SELECT * FROM temp_df")

if __name__ == "__main__":
    move_csv_to_duckdb_sql_with_context(csv_path, db_path, table_name)