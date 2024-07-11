import requests
import json
from airflow.models import Variable
import os


def save_json(data, file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_movies():
    API_KEY = Variable.get("api")
    page = int(Variable.get("cur_page"))
    limit = Variable.get("limit")
    print(page)
    print(API_KEY)

    response = requests.get(
        f"https://api.kinopoisk.dev/v1.4/movie?page={page}&limit={limit}&notNullFields=genres.name&type=movie&rating.kp=1-10",
        headers={"X-API-KEY": API_KEY}
    )

    if response.status_code == 200:
        movie_data = response.json()
        file_path = "dags/data/etl/movie_data.json"

        save_json(movie_data, file_path)
        print("Данные успешно сохранены в файл 'movie_data.json'.")
    else:
        print(f"Ошибка при получении данных: {response.status_code}")

    Variable.set("cur_page", str(page + 1))