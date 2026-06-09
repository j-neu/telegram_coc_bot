"""Dev utility: print all rows in the agreements table."""
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


def read_database():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM agreements ORDER BY agreed_at DESC;")
            rows = cur.fetchall()
            if not rows:
                print("No records found.")
                return
            headers = list(rows[0].keys())
            print(" | ".join(headers))
            print("-" * (len(" | ".join(headers))))
            for row in rows:
                print(" | ".join(str(v) for v in row.values()))
    finally:
        conn.close()


if __name__ == "__main__":
    read_database()
