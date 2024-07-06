def create_table():
    return '''CREATE TABLE IF NOT EXISTS movies (
            id SERIAL PRIMARY KEY,
            name VARCHAR,
            description VARCHAR,
            year INTEGER,
            rating FLOAT,
            votes INTEGER,
            movie_length INTEGER,
            age_rating VARCHAR,
            genres VARCHAR,
            countries VARCHAR
        )'''