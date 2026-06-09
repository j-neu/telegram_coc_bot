"""Dev utility: clear all rows from the agreements table."""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def clear_database():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM agreements;")
        conn.commit()
        print("All records cleared from agreements table.")
    finally:
        conn.close()


if __name__ == "__main__":
    clear_database()
