import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..config import settings
from ..models.document import Document
from ..schemas.document import DocumentResponse
from ..services.rag_service import rag_service

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

def run_background_ingest(document_id: str, file_path: str):
    """
    Background worker process to ingest the document.
    Create a new database session to avoid thread conflicts.
    """
    from ..database import SessionLocal
    db = SessionLocal()
    try:
        rag_service.ingest_document(db, document_id, file_path)
    finally:
        db.close()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_extensions = (".pdf", ".xlsx", ".xls", ".csv")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400, 
            detail=f"Only the following formats are supported: {', '.join(allowed_extensions)}"
        )

    # Generate unique ID and save file locally
    doc_id = str(uuid.uuid4())
    safe_filename = f"{doc_id}_{os.path.basename(file.filename)}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Register document in Database with status "processing"
    db_doc = Document(
        id=doc_id,
        filename=file.filename,
        file_path=file_path,
        status="processing",
        chunk_count=0
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    # Dispatch ingestion to background task
    background_tasks.add_task(run_background_ingest, doc_id, file_path)

    return db_doc

@router.get("", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    """Retrieve all uploaded documents."""
    return db.query(Document).order_by(Document.created_at.desc()).all()

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document, its database record, and its vector embeddings."""
    db_doc = db.query(Document).filter(Document.id == document_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # 1. Delete vector embeddings from ChromaDB
    rag_service.delete_document_vectors(document_id)

    # 2. Delete local PDF file if it exists
    if os.path.exists(db_doc.file_path):
        try:
            os.remove(db_doc.file_path)
        except Exception as e:
            print(f"Warning: Failed to delete physical file {db_doc.file_path}: {e}")

    # 3. Delete database record (cascading deletes the chunks as well)
    db.delete(db_doc)
    db.commit()

    return {"detail": "Document and associated vectors deleted successfully."}
