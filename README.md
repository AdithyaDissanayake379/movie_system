# Movie Rental Management System

Assessment implementation using Python, Tkinter and MySQL.

## Features
Employee login with bcrypt-hashed passwords; movie/customer CRUD and search; rental issue and return; configurable late fees; Excel reports; genre chart; keyboard-friendly tab navigation.

## Setup (Windows, VS Code)
1. Install Python 3.11+ and MySQL Server 8.0+, plus VS Code/Python extension.
2. Open this folder in VS Code. Run `py -m venv .venv` in PowerShell and activate with `.\.venv\Scripts\Activate.ps1` (or use `.venv\Scripts\python.exe` directly).
3. Run `python -m pip install -r requirements.txt`.
4. In MySQL Workbench, run `schema.sql` to create database/tables.
5. Create a dedicated MySQL account in Workbench as administrator:
   ```sql
   CREATE USER IF NOT EXISTS 'movie_app'@'localhost' IDENTIFIED BY 'CHOOSE_A_STRONG_LOCAL_PASSWORD';
   GRANT SELECT, INSERT, UPDATE, DELETE ON movie_rental.* TO 'movie_app'@'localhost';