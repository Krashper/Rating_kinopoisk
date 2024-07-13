import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import logging


def get_numpy_data(path: str):
    try:
        data = np.load(path)
        return data

    except Exception as e:
        logging.error("Error during getting numpy data: ", e)


def save_model(model, path, key):
    try:
        with open(path, 'wb') as f:
            pickle.dump(model, f)
            
        s3_hook = S3Hook(aws_conn_id='minio')
        s3_hook.load_file(filename=path, key=key, bucket_name="models", replace=True)
    
    except Exception as e:
        logging.error("Error during saving model into S3-bucket: ", e)


def get_metrics(y_pred, y_test):
    try:
        rmse = mean_squared_error(y_test, y_pred) ** 0.5
        mae = mean_absolute_error(y_test, y_pred)

        print("RMSE: ", rmse)
        print("MAE: ", mae)
    
    except Exception as e:
        logging.error("Error during getting model metrics: ", e)


def train_model():
    try:
        path = "dags/data/model_data/"

        X = get_numpy_data(path+"X.npy")
        y = get_numpy_data(path+"Y.npy")

        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        rfr = RandomForestRegressor(random_state=42)

        grid_space={'max_depth':[3,5,10,None],
                    'n_estimators':[10,100,200],
                    'max_features':[1,3,5,7],
                    'min_samples_leaf':[2, 3, 5],
                    'min_samples_split':[2, 3, 5]
                    }

        grid = GridSearchCV(rfr, param_grid=grid_space, cv=3, n_jobs=-1, 
                            scoring="neg_mean_squared_error", error_score='raise')
        grid.fit(x_train, y_train)

        print("Best Parameters:", grid.best_params_)
        print("Best Scoring:", grid.best_score_)

        best_model = grid.best_estimator_

        best_model.fit(x_train, y_train)


        key = f"predicted_model.pkl"
        model_path = path + key

        save_model(best_model, model_path, key)

        y_pred = best_model.predict(x_test)

        get_metrics(y_pred, y_test)
    
    except Exception as e:
        logging.error("Error during training model: ", e)