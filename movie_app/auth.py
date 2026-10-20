"""Employee password verification; plain-text passwords are never stored."""
import bcrypt
from movie_app.db import fetch_all, execute

def create_employee(username, password):
    if len(password) < 10 or not username.strip():
        raise ValueError("Username required and password must be at least 10 characters")
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return execute("INSERT INTO employees(username,password_hash) VALUES (%s,%s)",
                   (username.strip(), password_hash))

def authenticate(username, password):
    rows = fetch_all("SELECT password_hash FROM employees WHERE username=%s", (username.strip(),))
    return bool(rows) and bcrypt.checkpw(password.encode(), rows[0]["password_hash"].encode())