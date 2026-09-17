import os
import sys

# Adjust Python path to import app correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine

def migrate():
    print("Running database migration...")
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS title VARCHAR(255);"))
            print("Successfully added 'title' column to 'chat_sessions' table (if it did not already exist).")
    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    migrate()
