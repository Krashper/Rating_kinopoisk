from airflow.providers.postgres.hooks.postgres import PostgresHook
import logging


def get_data():
    try:
        hook = PostgresHook(postgres_conn_id='postgres')
        data = hook.get_pandas_df('SELECT * FROM movies')
            
        data.to_csv("dags/data/model_data/data_from_db.csv")
        return
    
    except Exception as e:
        logging.error("Error during getting data from database: ", e)