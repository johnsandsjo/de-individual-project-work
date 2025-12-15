import base64
import json
from google.cloud import bigquery
from google.cloud import storage 


PROJECT_ID = "gen-lang-client-0857764778" 
DATASET_ID = "prj_job_staging"

# --- Cloud Function Entry Point ---
def gcs_to_bigquery_loader(event, context):
    """
    Background Cloud Function triggered by Pub/Sub (GCS).
    Triggers a native BigQuery Load Job directly from the GCS URI.
    """
    print(f"Received Cloud Function trigger. Context: {context.event_id}")

    try:
        message_data = base64.b64decode(event['data']).decode('utf-8')
        gcs_payload = json.loads(message_data)

        # 2. EXTRACT THE FILE PATH
        bucket_name = gcs_payload.get('bucket')
        file_name = gcs_payload.get('name')

        gcs_uri = f"gs://{bucket_name}/{file_name}"
        print(f"Processing file: {gcs_uri}")

        # Derive table name from the file name (e.g., 'initial_test_run')
        table_name = file_name.split('/')[-1].split('.')[0]
        
        # 3. CONFIGURE AND RUN BIGQUERY LOAD JOB
        bq_client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=2, # Assuming your CSV has a header row
            autodetect=True,     # BigQuery infers the schema and column types
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND, # Appends data if table exists
        )

        # Start the load job
        load_job = bq_client.load_table_from_uri(
            gcs_uri,
            table_id,
            job_config=job_config
        )

        print(f"Starting BigQuery load job {load_job.job_id} for table {table_name}")
        load_job.result()  # Wait for the job to complete

        print(f"Load Job Completed. Loaded {load_job.output_rows} rows into {table_id}.")

    except Exception as e:
        print(f"An error occurred during BigQuery load: {e}")
        import traceback
        traceback.print_exc()
        raise e