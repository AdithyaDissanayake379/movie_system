"""Transactional movie checkout/return and rental search."""
from datetime import date
from decimal import Decimal
import os
from movie_app.db import connection, fetch_all

RENTAL_LIST = """SELECT r.rental_id,r.movie_id,m.title,r.customer_id,c.name,
  r.rental_date,r.due_date,r.return_date,r.late_fee
  FROM rentals r JOIN movies m ON r.movie_id=m.movie_id
  JOIN customers c ON r.customer_id=c.customer_id"""

def late_fee(due_date, return_date, daily_fee=Decimal("100.00")):
    days = max(0, (return_date - due_date).days)
    return (daily_fee * days).quantize(Decimal("0.01"))

def rent(movie_id, customer_id, rental_date, due_date):
    start, due = date.fromisoformat(str(rental_date)), date.fromisoformat(str(due_date))
    if due < start:
        raise ValueError("Due date must not precede rental date")
    with connection() as db:
        cur = db.cursor(dictionary=True)
        try:
            # Lock the movie to serialize concurrent checkouts of the same item.
            cur.execute("SELECT movie_id FROM movies WHERE movie_id=%s FOR UPDATE", (int(movie_id),))
            if not cur.fetchone():
                raise ValueError("Movie ID does not exist")
            cur.execute("SELECT customer_id FROM customers WHERE customer_id=%s", (int(customer_id),))
            if not cur.fetchone():
                raise ValueError("Customer ID does not exist")
            cur.execute("SELECT rental_id FROM rentals WHERE movie_id=%s AND return_date IS NULL LIMIT 1",
                        (int(movie_id),))
            if cur.fetchone():
                raise ValueError("Movie is already rented out")
            cur.execute("INSERT INTO rentals(movie_id,customer_id,rental_date,due_date) VALUES (%s,%s,%s,%s)",
                        (int(movie_id), int(customer_id), start, due))
            return cur.lastrowid
        finally:
            cur.close()

def return_movie(rental_id, returned_on):
    returned = date.fromisoformat(str(returned_on))
    daily = Decimal(os.getenv("LATE_FEE_PER_DAY", "100"))
    with connection() as db:
        cur = db.cursor(dictionary=True)
        try:
            cur.execute("SELECT rental_date,due_date,return_date FROM rentals WHERE rental_id=%s FOR UPDATE",
                        (int(rental_id),))
            record = cur.fetchone()
            if not record or record["return_date"] is not None:
                raise ValueError("No active rental with this ID")
            if returned < record["rental_date"]:
                raise ValueError("Return cannot precede rental date")
            fee = late_fee(record["due_date"], returned, daily)
            cur.execute("UPDATE rentals SET return_date=%s,late_fee=%s WHERE rental_id=%s",
                        (returned, fee, int(rental_id)))
            return fee
        finally:
            cur.close()

def search(text="", issue_date="", return_date=""):
    sql = RENTAL_LIST + " WHERE (m.title LIKE %s OR c.name LIKE %s)"
    params = [f"%{text}%"] * 2
    if str(issue_date).strip():
        sql += " AND r.rental_date=%s"
        params.append(date.fromisoformat(issue_date))
    if str(return_date).strip():
        sql += " AND r.return_date=%s"
        params.append(date.fromisoformat(return_date))
    return fetch_all(sql + " ORDER BY r.rental_id DESC", tuple(params))