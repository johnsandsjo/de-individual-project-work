import dlt
import requests
import json
from datetime import datetime



def _get_ads(url, params, headers):
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()  # check for http errors
    return json.loads(response.content.decode('utf8'))

@dlt.resource(table_name = "prj_daily_job_ads",write_disposition="replace")
def jobsearch_resource():
    date_str = datetime.now()
    today_date = date_str.strftime("%Y-%m-%d")
    url = "https://jobstream.api.jobtechdev.se/stream"
    params = {
        'date': f"{today_date}T00:00:00",
        "occupation-concept-id": {"6Hq3_tKo_V57", "apaJ_2ja_LuF"}
        }
    headers = {
        'accept': 'application/json'
        }    
    data = _get_ads(url, params=params, headers=headers)
    
    for ad in data:
        yield ad
            
@dlt.source
def job_ads_source():
    return jobsearch_resource()
