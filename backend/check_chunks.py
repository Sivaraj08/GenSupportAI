from app.database import SessionLocal
from app.models.document import Document, DocumentChunk

db = SessionLocal()
doc = db.query(Document).filter(Document.filename == "admission_support_system.pdf").first()
if doc:
    print(f"Document: {doc.filename}, ID: {doc.id}, Status: {doc.status}, Chunk count: {doc.chunk_count}")
    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
    for idx, chunk in enumerate(chunks):
        print(f"\n--- Chunk {idx+1} (Ref: {chunk.vector_ref}) ---")
        print(chunk.content)
else:
    print("admission_support_system.pdf not found in database.")
db.close()
