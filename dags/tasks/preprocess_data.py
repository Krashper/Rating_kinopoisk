import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
import pickle
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import logging


def get_data():
    try:
        data = pd.read_csv("dags/data/model_data/data_from_db.csv", index_col=0)
        return data
    
    except Exception as e:
        logging.error("Error during getting data: ", e)


def engineer_features(data):
    try:
        data["decade"] = data["year"].apply(lambda x: str(x // 10 * 10) + "-е")

        data['genres'] = data['genres'].str.split('|')

        data['countries'] = data['countries'].str.split('|')

        return data
    
    except Exception as e:
        logging.error("Error during engineering features: ", e)


def delete_missings(data, data_countries, data_genres):
    try:
        data = data.replace(0, np.NaN)


        data = data[~np.isnan(data["age_rating"])]


        mean_movie_length = int(data["movie_length"].mean())
        data["movie_length"] = data["movie_length"].fillna(mean_movie_length)


        data["description"] = data["description"].fillna("")

        mode_country = data_countries["countries"].mode()[0] # для замены -1 на моду признака

        data["countries"] = data["countries"].apply(lambda x: [mode_country] if "0" in str(x) else x)


        mode_genre = data_genres["genres"].mode()[0] # для замены -1 на моду признака

        data["genres"] = data["genres"].apply(lambda x: [mode_genre] if "0" in str(x) else x)

        return data
    
    except Exception as e:
        logging.error("Error during deleting missings from data: ", e)


def save_model(model, path, key):
    try:
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        
        s3_hook = S3Hook(aws_conn_id='minio')
        s3_hook.load_file(filename=path, key=key, bucket_name="models", replace=True)
    
    except Exception as e:
        logging.error("Error during saving model into S3-bucket: ", e)


def convert_to_binary_feature(data, feature: str):
    try:
        le = LabelEncoder()

        decade_list = sorted(data[feature].unique())

        le.fit(decade_list)

        data[f"{feature}_transformed"] = le.transform(data[feature])

        key = f"label_encoder_{feature}.pkl"
        path = "dags/data/model_data/" + key

        save_model(le, path, key)

        return data
    
    except Exception as e:
        logging.error("Error during converting features to binary features: ", e)


def standardize_features(data, features: list[str]):
    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(data[features])

        key = f"standart_scaler.pkl"
        path = "dags/data/model_data/" + key

        save_model(scaler, path, key)

        return X_scaled

    except Exception as e:
        logging.error("Error during standardizing features: ", e)

def compress_features(X):
    try:
        pca = PCA()
        pca.fit(X)


        cumsum = np.cumsum(pca.explained_variance_ratio_)

        d = np.argmax(cumsum >= 0.95) + 1


        pca = PCA(n_components=d)

        X_pca = pca.fit_transform(X)

        key = f"pca.pkl"
        path = "dags/data/model_data/" + key

        save_model(pca, path, key)

        return X_pca
    
    except Exception as e:
        logging.error("Error during applying PCA to the data")


def save_to_numpy(data, path: str):
    try:
        np.save(path, data)
        return

    except Exception as e:
        logging.error("Error during saving file as numpy: ", e)



def preprocess_data():
    try:
        data = get_data()

        data = engineer_features(data)

        data_genres = data.explode('genres')
        data_countries = data.explode("countries")

        data = delete_missings(data, data_countries, data_genres)

        unique_genres = data_genres["genres"].unique()

        # Преобразуем к строчному виду
        unique_genres = unique_genres.astype(str)

        unique_genres = unique_genres[unique_genres != "0"]

        save_to_numpy(unique_genres, "dags/data/model_data/genres.npy")


        def get_binary_genre(genre: str):
            data.loc[:, genre] = data["genres"].apply(lambda x: 1 if genre in x else 0)
            print("Добавлен жанр: ", genre)

        for genre in unique_genres:
            get_binary_genre(genre)


        unique_countries = data_countries["countries"].unique()

        # Преобразуем к строчному виду
        unique_countries = unique_countries.astype(str)

        unique_countries = unique_countries[unique_countries != "0"]

        save_to_numpy(unique_countries, "dags/data/model_data/countries.npy")


        def get_binary_country(country: str):
            float_rows = data[data['countries'].apply(lambda x: isinstance(x, float))]
            print(float_rows)

            data.loc[:, country] = data["countries"].apply(lambda x: 1 if country in x else 0)
            print("Добавлена страна: ", country)

        for country in unique_countries:
            get_binary_country(country)


        data = convert_to_binary_feature(data, "decade")

        data = convert_to_binary_feature(data, "age_rating")


        X_cols = ["votes", "movie_length", "decade_transformed", "age_rating_transformed"]

        X_cols.extend(unique_genres.tolist())
        X_cols.extend(unique_countries.tolist())


        X_scaled = standardize_features(data, ["votes", "movie_length"])

        X_cols.remove("votes")
        X_cols.remove("movie_length")

        X = np.hstack((X_scaled, data[X_cols].values))

        X_pca = compress_features(X)

        y = data["rating"]

        save_to_numpy(X_pca, "dags/data/model_data/X.npy")

        save_to_numpy(y, "dags/data/model_data/Y.npy")

        return
    
    except Exception as e:
        logging.error("Error during preprocessing data: ", e)