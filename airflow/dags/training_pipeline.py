# This code is from airflow
from asyncio import tasks
import json
from textwrap import dedent
import pendulum
import os
from airflow import DAG           # To schedule anything in airflow you need you define a DAG for it
from airflow.operators.python import PythonOperator


with DAG(                         # Directed Acyclic Graph
    'sensor_training',            # Name for DAG
    default_args={'retries': 2},  # No of retries for pipeline, if pipeline 1st time fails it will try for second, after that it is a failure
    # [END default_args]
    description='Sensor Fault Detection',
    schedule_interval="@weekly",  # Pipeline will run weekly basis
    start_date=pendulum.datetime(2022, 12, 30, tz="UTC"),   # Start date for pipeline
    catchup=False,              # Flag relation to previous run
    tags=['example'],           # list of string
) as dag:

    
    def training(**kwargs):
        from sensor.pipeline.training_pipeline import start_training_pipeline    # Starting training pipeline from sensor
        start_training_pipeline()
    
    def sync_artifact_to_s3_bucket(**kwargs):                                    # Storing artifacts and models to S3 bucket
        bucket_name = os.getenv("BUCKET_NAME")
        os.system(f"aws s3 sync /app/artifact s3://{bucket_name}/artifacts")
        os.system(f"aws s3 sync /app/saved_models s3://{bucket_name}/saved_models")

    training_pipeline  = PythonOperator(               # We are using python operator to call training function
            task_id="train_pipeline",                  # so that when we will run this code from airflow pipeline 
            python_callable=training                   # it will trigger training pipeline

    )

    sync_data_to_s3 = PythonOperator(                  # Calling using python operator
            task_id="sync_data_to_s3",
            python_callable=sync_artifact_to_s3_bucket

    )

    training_pipeline >> sync_data_to_s3                # The flow of execution