import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
import pickle
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


def get_data():
    data = pd.read_csv("dags/data/model_data/data_from_db.csv", index_col=0)
    return data


def engineer_features(data):
    data["decade"] = data["year"].apply(lambda x: str(x // 10 * 10) + "-е")

    data['genres'] = data['genres'].str.split('|')

    data['countries'] = data['countries'].str.split('|')

    return data


def delete_missings(data):
    data = data.replace(-1, np.NaN)


    data = data[~np.isnan(data["age_rating"])]


    mean_movie_length = int(data["movie_length"].mean())
    data["movie_length"] = data["movie_length"].fillna(mean_movie_length)


    data["description"] = data["description"].fillna("")

    return data


def save_model(model, path, key):
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    
    s3_hook = S3Hook(aws_conn_id='minio')
    s3_hook.load_file(filename=path, key=key, bucket_name="models", replace=True)


def convert_to_binary_feature(data, feature: str):
    le = LabelEncoder()

    decade_list = sorted(data[feature].unique())

    le.fit(decade_list)

    data[f"{feature}_transformed"] = le.transform(data[feature])

    key = f"label_encoder_{feature}.pkl"
    path = "dags/data/model_data/" + key

    save_model(le, path, key)

    return data


def standardize_features(data, features: list[str]):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data[features])

    key = f"standart_scaler.pkl"
    path = "dags/data/model_data/" + key

    save_model(scaler, path, key)

    return X_scaled


def compress_features(X):
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


def save_to_numpy(data, path: str):
    np.save(path, data)
    return



def preprocess_data():
    data = get_data()

    data = engineer_features(data)

    data_genres = data.explode('genres')
    data_countries = data.explode("countries")

    data = delete_missings(data)

    unique_genres = data_genres["genres"].unique()

    save_to_numpy(unique_genres, "dags/data/model_data/genres.npy")


    def get_binary_genre(genre: str):
        data.loc[:, genre] = data["genres"].apply(lambda x: 1 if genre in x else 0)
        print("Добавлен жанр: ", genre)

    for genre in unique_genres:
        get_binary_genre(genre)


    unique_countries = data_countries["countries"].unique()

    mode_country = data_countries["countries"].mode()[0] # для замены -1 на моду признака

    data["countries"] = data["countries"].apply(lambda x: [mode_country] if "-1" in x else x)

    unique_countries = unique_countries[unique_countries != "-1"]

    save_to_numpy(unique_countries, "dags/data/model_data/countries.npy")


    def get_binary_country(country: str):
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