import dlt
import requests
import json
from pathlib import Path
import os


db_path = str(Path(__file__).parents[1] / "data_warehouse/prj_job_advertisements.duckdb")

def _get_ads(url):
    response = requests.get(url)
    response.raise_for_status()  # check for http errors
    return json.loads(response.content)

@dlt.resource(write_disposition="replace")
def jobsearch_resource():
    url = "https://jobstream.api.jobtechdev.se/snapshot"
    
    data = _get_ads(url)
    target_occupation_ids = {"6Hq3_tKo_V57", "apaJ_2ja_LuF"}
    for ad in data:
        if ad["occupation_field"]["concept_id"] in target_occupation_ids:
            yield ad

def run_pipeline(table_name):
    pipeline = dlt.pipeline(
        pipeline_name="prj_job_ads_bulk_update",
        destination=dlt.destinations.duckdb(db_path),
        dataset_name="staging",
    )
        
    load_info = pipeline.run(jobsearch_resource(), table_name=table_name)
    print(load_info)


if __name__ == "__main__":
    working_directory = Path(__file__).parent
    os.chdir(working_directory)

    table_name = "prj_job_ads_bulk"

    run_pipeline(table_name=table_name)