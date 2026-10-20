"""Database connections and query helpers (parameterized statements)."""
import os
from contextlib import contextmanager
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

@contextmanager
def connection():
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "movie_app"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "movie_rental"),
    )
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def fetch_all(sql, params=()):
    with connection() as db:
        cur = db.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            cur.close()

def execute(sql, params=()):
    with connection() as db:
        cur = db.cursor()
        try:
            cur.execute(sql, params)
            return cur.lastrowid or cur.rowcount
        finally:
            cur.close()