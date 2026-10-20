
from movie_app.db import connection

try:
    with connection() as db:
        print("MySQL connected successfully!")

        cursor = db.cursor()
        cursor.execute("SELECT DATABASE()")
        database = cursor.fetchone()

        print("Connected database:", database[0])
        cursor.close()

except Exception as error:
    print("Database connection failed!")
    print("Error:", error)
