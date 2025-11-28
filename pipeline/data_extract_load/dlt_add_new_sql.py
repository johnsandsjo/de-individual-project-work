import dlt
from pathlib import Path
import pandas as pd
import os

db_path = str(Path(__file__).parents[1] / "data_warehouse/prj_job_advertisements.duckdb")
data_path = Path(__file__).parents[1] / "agent_script/data"

@dlt.resource(write_disposition="replace")
def csv_resource():
    df = pd.read_csv(data_path / "scb_stats.csv", skiprows=2, encoding='latin1')
    serialized_csv = df.to_dict(orient='records')
    for i, row in enumerate(serialized_csv):
        yield row

def run_pipeline(table_name):
    pipeline = dlt.pipeline(
        pipeline_name="add_csv_source",
        destination=dlt.destinations.duckdb(db_path),
        dataset_name="staging",
    )
        
    load_info = pipeline.run(csv_resource(), table_name=table_name)
    print(load_info)


if __name__ == "__main__":
    table_name = "scb_stats"
    run_pipeline(table_name=table_name)
    