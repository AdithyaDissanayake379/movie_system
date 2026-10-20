"""Customer CRUD and name/ID search."""
from movie_app.db import execute, fetch_all

def validate(name, contact):
    if not name.strip() or not contact.strip():
        raise ValueError("Customer name and contact are required")
    if len(name) > 150 or len(contact) > 200:
        raise ValueError("Input is too long")
    return name.strip(), contact.strip()

def add(name, contact):
    return execute("INSERT INTO customers(name,contact) VALUES (%s,%s)", validate(name, contact))

def update(customer_id, name, contact):
    return execute("UPDATE customers SET name=%s,contact=%s WHERE customer_id=%s",
                   (*validate(name, contact), int(customer_id)))

def delete(customer_id):
    return execute("DELETE FROM customers WHERE customer_id=%s", (int(customer_id),))

def search(text=""):
    text = str(text).strip()
    return fetch_all("SELECT * FROM customers WHERE name LIKE %s OR CAST(customer_id AS CHAR) LIKE %s ORDER BY customer_id DESC",
                     (f"%{text}%", f"%{text}%"))