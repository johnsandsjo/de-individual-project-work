from google.cloud import bigquery
from google.cloud import storage 
import os
import base64
import json


# --- Cloud Function Entry Point ---
def gcs_to_bigquery_loader(event, context):
    """
    Triggered by a change to a Cloud Storage bucket.
    """
    # 1. Get file details from the event
    file_name = event['name']
    bucket_name = event['bucket']
    uri = f"gs://{bucket_name}/{file_name}"

    # 2. Configuration
    project_id = os.environ.get('PROJECT_ID')
    dataset_id = "staging"
    # Derive table name from the file name (e.g., 'initial_test_run')
    table_name = file_name.split('/')[-1].split('.')[0]
    table_id = f"{table_name}"

    client = bigquery.Client()
    table_ref = client.dataset(dataset_id).table(table_id)

    # 3. Configure the Load Job
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.CSV,
        autodetect=True,  # Automatically detects schema from CSV header
        skip_leading_rows=1, # Skip header row
    )
    # 4. Run the Job
    try:
        load_job = client.load_table_from_uri(
            uri, table_ref, job_config=job_config
        )
        print(f"Starting job {load_job.job_id} for file {file_name}")
        load_job.result()  # Wait for the job to complete
        print("Job finished successfully.")
    except Exception as e:
        print(f"Error loading {file_name}: {e}")