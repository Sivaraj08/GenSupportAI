import os
import sys
import uuid

# Adjust Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force SQLite if PostgreSQL is not available
if "DATABASE_URL" not in os.environ:
    # If there's an env setting in .env we can read it, but if postgres connection fails, we fallback to sqlite.
    # To keep local development running smoothly, we set SQLite database path:
    os.environ["DATABASE_URL"] = "sqlite:///./gensupport.db"
    print("Database URL not specified in environment. Defaulting to local SQLite database: ./gensupport.db")

from app.database import engine, Base, SessionLocal
from app.models.document import Document, DocumentChunk
from app.services.rag_service import rag_service
from create_admissions_pdf import generate_pdf

def run_ingestion():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Paths
    pdf_filename = "admission_support_system.pdf"
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    pdf_path = os.path.join(uploads_dir, pdf_filename)
    
    # 1. Generate the PDF
    print(f"Generating PDF at {pdf_path}...")
    generate_pdf(pdf_path)
    
    # 2. Check and clean up previous records with this filename
    print(f"Checking for existing database records for {pdf_filename}...")
    existing_docs = db.query(Document).filter(Document.filename == pdf_filename).all()
    if existing_docs:
        print(f"Found {len(existing_docs)} previous documents. Cleaning up...")
        for doc in existing_docs:
            print(f" - Deleting vectors and record for document ID: {doc.id}")
            rag_service.delete_document_vectors(doc.id)
            db.delete(doc)
        db.commit()
        print("Cleanup completed.")
        
    # 3. Register document in database with status "processing"
    doc_id = str(uuid.uuid4())
    print(f"Registering new document in database: ID={doc_id}, filename={pdf_filename}")
    
    db_doc = Document(
        id=doc_id,
        filename=pdf_filename,
        file_path=pdf_path,
        status="processing",
        chunk_count=0
    )
    db.add(db_doc)
    db.commit()
    
    # 4. Ingest the document
    print("Running RAG ingestion pipeline...")
    success = rag_service.ingest_document(db, doc_id, pdf_path)
    
    if success:
        db.refresh(db_doc)
        print(f"\n--- SUCCESS ---")
        print(f"Document filename: {db_doc.filename}")
        print(f"Document ID: {db_doc.id}")
        print(f"Final Status: {db_doc.status}")
        print(f"Chunks Indexed: {db_doc.chunk_count}")
    else:
        print(f"\n--- ERROR ---")
        print(f"RAG ingestion failed for document ID: {doc_id}")
        sys.exit(1)
        
    db.close()

if __name__ == "__main__":
    run_ingestion()
