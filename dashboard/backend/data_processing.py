import pandas as pd 
from pathlib import Path
import json
from dotenv import load_dotenv
from google.cloud import bigquery
import os

load_dotenv()

def query_job_listings(occupational_field):
    client = bigquery.Client()

    if occupational_field == "Data/IT":
        table_id = "grad-work-john.marts.mart_data_it"
    elif occupational_field == "Säkerhet och bevakning":
        table_id = "grad-work-john.marts.mart_safety"
    else:
        table_id = "grad-work-john.marts.mart_social_work"
    
    query = f"SELECT * FROM `{table_id}`"

    return client.query(query).to_dataframe()
    
    
def read_json_data():
    working_directory = Path(__file__).parent

    path_geojson = working_directory / "geojson_data"

    with open(path_geojson / "swedish_regions.geojson", "r", encoding= "utf-8") as file:
        json_data = json.load(file)
        
    return json_data

