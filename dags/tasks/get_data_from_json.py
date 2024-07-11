import pandas as pd
import json


def get_row(movie: dict) -> list:
    id = movie["id"]
    name = str(movie["name"]).replace("'", "")
    description = str(movie["description"]).replace("'", "")
    year = movie["year"]
    rating = movie["rating"]["kp"]
    votes = movie["votes"]["kp"]
    movie_length = movie["movieLength"]
    age_rating = movie["ageRating"]
    try:
        genres = "|".join([genre["name"] for genre in movie["genres"]])

    except KeyError:
        genres = None

    try:
        countries = "|".join([country["name"] for country in movie["countries"]])
    
    except KeyError:
        countries = None

    row = [id, name, description, year, 
              rating, votes, movie_length, age_rating, genres, countries]
    
    return row


def get_data_from_json():
    with open("dags/data/etl/movie_data.json", encoding="utf-8") as f:
        data = json.load(f)

    columns = ["id", "name", "description", "year", "rating", "votes", "movie_length", 
                "age_rating", "genres", "countries"]

    dataset = pd.DataFrame(columns=columns)

    for movie in data["docs"]:
        row = get_row(movie)
        
        dataset.loc[len(dataset.index)] = row
    
    dataset = dataset.fillna(-1)

    dataset.to_csv("dags/data/etl/dataset.csv")