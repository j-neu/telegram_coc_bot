import sqlite3
import os

DB_FILE = "coc_agreements.db"

def clear_database():
    """Connects to the SQLite database and deletes all agreements."""
    if not os.path.exists(DB_FILE):
        print(f"Database file not found: {DB_FILE}")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        print(f"Successfully connected to {DB_FILE}")

        # Delete all rows from the agreements table
        cursor.execute("DELETE FROM agreements;")
        
        # Reset the auto-incrementing ID
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='agreements';")

        conn.commit()
        
        print("All records have been cleared from the 'agreements' table.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    clear_database()