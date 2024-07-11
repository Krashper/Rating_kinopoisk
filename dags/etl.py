from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from tasks.get_movies import get_movies
from tasks.get_data_from_json import get_data_from_json
from tasks.sql.create_table import create_table
from tasks.sql.insert_data import insert_data
from tasks.check_max_page import check_max_page


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 23),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="create_movie_dataset_v47",
    description="It is a dag which gets data from HeadHunter and preprocesses them",
    start_date=datetime(2024, 1, 1),
    schedule_interval="*/10 * * * *",
    catchup=False,
    default_args=default_args
) as dag:
    start_dag_task = ShortCircuitOperator(
        task_id="start_dag",
        python_callable=check_max_page
    )

    get_json_task = PythonOperator(
        task_id="get_json",
        python_callable=get_movies
    )


    get_data_from_json_task = PythonOperator(
        task_id="get_data_from_json",
        python_callable=get_data_from_json
    )

    # 
    create_table_task = PostgresOperator(
        task_id='create_movies_table',
        postgres_conn_id="postgres",
        sql=create_table()
    )

    insert_data_to_db_task = PostgresOperator(
        task_id="insert_data_to_db",
        postgres_conn_id="postgres",
        sql=insert_data()
    )


    start_dag_task >> get_json_task
    get_json_task >> [get_data_from_json_task, create_table_task]
    get_data_from_json_task >> insert_data_to_db_task
    create_table_task >> insert_data_to_db_task