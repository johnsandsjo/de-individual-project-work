from google.cloud import bigquery
import os

def query_data_warehouse(table_name : str):
    """
    Query BigQuery warehouse
    """
    #Configuration
    project_id = os.environ.get('PROJECT_ID')
    dataset_id = "staging"
    table_id = f"{table_name}"

    client = bigquery.Client()
    table_ref = client.dataset(dataset_id).table(table_id)

    sql = f"""
    SELECT *
    FROM `{table_ref}`
    """
    query_job = client.query(sql)
    df = query_job.to_dataframe()
    return df.columns

if __name__ == "__main__":
    warehouse_data = query_data_warehouse("cheap_house") # test csv
    print(warehouse_data)
