"""Run after schema.sql to create an employee account."""
import getpass
from movie_app.auth import create_employee

if __name__ == "__main__":
    username = input("New employee username: ").strip()
    password = getpass.getpass("Password (10+ chars): ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        raise SystemExit("Passwords do not match")
    create_employee(username, password)
    print("Employee created successfully")