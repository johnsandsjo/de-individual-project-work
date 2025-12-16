from google.cloud import bigquery
import os

def query_data_warehouse(table_name : str):
    """
    Query BigQuery warehouse
    """
    #Configuration
    project_id = os.environ.get('PROJECT_ID', 'grad-work-john')
    dataset_id = "raw"

    client = bigquery.Client(project=project_id, location="EU")

    sql = f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}`"

    try:
        query_job = client.query(sql)
        df = query_job.to_dataframe()
        return str(df.columns)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    warehouse_data = query_data_warehouse("cheap_house") # test csv
    print(warehouse_data)
