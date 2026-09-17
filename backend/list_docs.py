from app.database import SessionLocal
from app.models.document import Document

db = SessionLocal()
docs = db.query(Document).all()
print(f"Total documents: {len(docs)}")
for doc in docs:
    print(f"ID: {doc.id} | Filename: {doc.filename} | Status: {doc.status} | Chunks: {doc.chunk_count}")
db.close()
