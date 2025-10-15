import sqlite3

DB_FILE = "coc_agreements.db"

def read_database():
    """Connects to the SQLite database and prints all agreements."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print(f"Successfully connected to {DB_FILE}")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if not tables:
            print("No tables found in the database.")
            return

        for table_name in tables:
            table_name = table_name[0]
            print(f"\nContents of table: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            print(" | ".join(columns))
            print("-" * (len(" | ".join(columns))))
            
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            if not rows:
                print("No data in this table.")
            else:
                for row in rows:
                    print(" | ".join(map(str, row)))

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    read_database()