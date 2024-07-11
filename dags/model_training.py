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



# def upload_to_yandex():
#     connection = BaseHook.get_connection("yandex_storage_conn")
#     access_key = connection.login
#     secret_key = connection.password
#     bucket_name = "mlflow-kinopoisk"
#     local_file_path = "dags/data/data_from_db.csv"
#     yandex_file_path = "data/data_from_db.csv"

#     try:
#         s3 = boto3.client('s3',
#                           endpoint_url='https://storage.yandexcloud.net',
#                           aws_access_key_id=access_key,
#                           aws_secret_access_key=secret_key)

#         s3.upload_file(local_file_path, bucket_name, yandex_file_path)
#         print("File uploaded successfully to Yandex Object Storage")

#     except NoCredentialsError:
#         print("Credentials not available")


# def main():
#     mlflow.set_experiment("my-experiment-2")
#     mlflow.set_tracking_uri("https://host.docker.internal:5000")

#     # Генерация случайных данных
#     X = np.random.rand(100, 1)
#     y = 2 * X + 3 + np.random.normal(0, 0.1, (100, 1))

#     # Обучение модели
#     model = LinearRegression()
#     model.fit(X, y)

#     # Логирование метрик и параметров
#     with mlflow.start_run():
#         mlflow.log_param("alpha", 0.01)
#         mlflow.log_metric("r2", model.score(X, y))
#         mlflow.sklearn.log_model(model, "model2")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 23),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def test_postgres_connection():
    try:
        connection = psycopg2.connect(
            dbname='ETL',
            user='postgres',
            password='86754231qaZ',
            host='host.docker.internal',
            port='5432'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")
        cursor.close()
        connection.close()
    except Exception as error:
        print(f"Error connecting to PostgreSQL: {error}")

with DAG(
    dag_id="model_training_v82",
    description="It is a dag which gets data from HeadHunter and preprocesses them",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args
) as dag:
    # def get_data():
    #     hook = PostgresHook(postgres_conn_id='postgres')
    #     data = hook.get_pandas_df('SELECT * FROM movies')
        
    #     data.to_csv("dags/data/data_from_db.csv")
    #     return


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
    # train_model_task = PythonOperator(
    #     task_id='train_model',
    #     python_callable=main,
    # )

    # train_model_task
    
