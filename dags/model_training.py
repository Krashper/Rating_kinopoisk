from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from tasks.get_data_from_db import get_data
from tasks.create_bucket import create_bucket
from tasks.preprocess_data import preprocess_data
from tasks.train_model import train_model
from airflow.hooks.base import BaseHook
import boto3
from botocore.exceptions import NoCredentialsError
import os
import psycopg2

import numpy as np
from sklearn.linear_model import LinearRegression


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 23),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="model_training_v91",
    description="It is a dag which trains the model for movie rating predictions",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args
) as dag:
    create_bucket_task = PythonOperator(
        task_id='create_bucket',
        python_callable=create_bucket,
        op_kwargs={
            "bucket_name": "models"
        }
    )

    get_data_task = PythonOperator(
        task_id="get_data",
        python_callable=get_data
    )

    preprocess_data_task = PythonOperator(
        task_id="preprocess_data",
        python_callable=preprocess_data
    )

    train_model_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model
    )
   
    create_bucket_task >> get_data_task >> preprocess_data_task >> train_model_task
    
