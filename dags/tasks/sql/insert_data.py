import pandas as pd


def insert_data():
    try:
        dataset = pd.read_csv("dags/data/dataset.csv", index_col=0, na_values=['nan', 'N/A'])

        print(dataset)
        insert_queries = []
        for _, row in dataset.iterrows():
            values = (row["id"], row['name'], str(row['description']).strip(), 
                    row['year'], row['rating'], 
                    row['votes'], row['movie_length'], row['age_rating'], 
                    row['genres'], row['countries'])
            insert_queries.append(
                f"INSERT INTO movies (id, name, description, year, rating, votes, movie_length, age_rating, genres, countries) VALUES ({values[0]}, '{values[1]}', '{values[2]}', {values[3]}, {values[4]}, {values[5]}, {values[6]}, '{values[7]}', '{values[8]}', '{values[9]}') ON CONFLICT DO NOTHING")

        return ";\n".join(insert_queries)

    except Exception as e:
        print(e)
        return