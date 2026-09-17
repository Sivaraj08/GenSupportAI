import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Force DATABASE_URL to use postgres
os.environ["DATABASE_URL"] = "postgresql://postgres:supersecretpassword@localhost:5432/postgres"

from app.database import SessionLocal
from app.models.document import Document

db = SessionLocal()
try:
    docs = db.query(Document).all()
    print(f"Total documents in Postgres: {len(docs)}")
    for doc in docs:
        print(f"ID: {doc.id} | Filename: {doc.filename} | Status: {doc.status} | Chunks: {doc.chunk_count}")
except Exception as e:
    print(f"Error querying Postgres: {e}")
db.close()
