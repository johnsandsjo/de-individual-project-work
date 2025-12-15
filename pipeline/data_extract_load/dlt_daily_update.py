import dlt
import requests
import json
from datetime import datetime
from pathlib import Path
import os

def _get_ads(url, params, headers):
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()  # check for http errors
    return json.loads(response.content.decode('utf8'))

@dlt.resource(write_disposition="replace")
def jobsearch_resource():
    date_str = datetime.now()
    today_date = date_str.strftime("%Y-%m-%d")
    url = "https://jobstream.api.jobtechdev.se/stream"
    params = {
        'date': f"{today_date}T00:00:00",
        "occupation-concept-id": {"6Hq3_tKo_V57", "apaJ_2ja_LuF", "GazW_2TU_kJw", "E7hm_BLq_fqZ"}
        }
    headers = {
        'accept': 'application/json'
        }    
    data = _get_ads(url, params=params, headers=headers)
    
    for ad in data:
        yield ad

def run_pipeline(table_name):
    pipeline = dlt.pipeline(
        pipeline_name="job_ads_stream_daily",
        destination="bigquery",
        dataset_name="staging",
    )
        
    load_info = pipeline.run(jobsearch_resource(), table_name=table_name)
    print(load_info)


if __name__ == "__main__":
    working_directory = Path(__file__).parent
    os.chdir(working_directory)

    table_name = "prj_daily_job_ads"

    run_pipeline(table_name=table_name)