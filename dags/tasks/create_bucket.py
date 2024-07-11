from minio import Minio
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import logging


def create_bucket(bucket_name: str):
    try:
        hook = S3Hook(aws_conn_id="minio")

        # Создание нового bucket
        hook.create_bucket(bucket_name="models")

        return
    
    except Exception as e:
        logging.error("Ошибка во время создания bucket: ", e)
    