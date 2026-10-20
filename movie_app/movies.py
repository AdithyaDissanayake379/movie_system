"""Movie create/read/update/delete/search operations."""
from movie_app.db import execute, fetch_all

def validate(title, genre, year, price, producer):
    if not all([title.strip(), genre.strip(), producer.strip()]):
        raise ValueError("Title, genre and producer are required")
    year = int(year)
    price = float(price)
    if not 1888 <= year <= 2100 or price < 0:
        raise ValueError("Invalid release year or rental price")
    return title.strip(), genre.strip(), year, round(price, 2), producer.strip()

def add(title, genre, year, price, producer):
    return execute("INSERT INTO movies(title,genre,release_year,rental_price,producer) VALUES (%s,%s,%s,%s,%s)",
                   validate(title, genre, year, price, producer))

def update(movie_id, title, genre, year, price, producer):
    return execute("UPDATE movies SET title=%s,genre=%s,release_year=%s,rental_price=%s,producer=%s WHERE movie_id=%s",
                   (*validate(title, genre, year, price, producer), int(movie_id)))

def delete(movie_id):
    # Historical rentals are preserved: MySQL FK RESTRICT blocks deletion.
    return execute("DELETE FROM movies WHERE movie_id=%s", (int(movie_id),))

def search(text="", year="", min_price="", max_price=""):
    sql = "SELECT * FROM movies WHERE (title LIKE %s OR genre LIKE %s OR producer LIKE %s)"
    params = [f"%{text}%"] * 3
    if str(year).strip():
        sql += " AND release_year=%s"
        params.append(int(year))
    if str(min_price).strip():
        sql += " AND rental_price >= %s"
        params.append(float(min_price))
    if str(max_price).strip():
        sql += " AND rental_price <= %s"
        params.append(float(max_price))
    return fetch_all(sql + " ORDER BY movie_id DESC", tuple(params))