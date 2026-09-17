from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class DocumentChunkBase(BaseModel):
    content: str
    vector_ref: str

class DocumentChunkCreate(DocumentChunkBase):
    pass

class DocumentChunk(DocumentChunkBase):
    id: str
    document_id: str

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    filename: str
    file_path: str
    status: str
    chunk_count: int

class DocumentCreate(BaseModel):
    filename: str
    file_path: str

class Document(DocumentBase):
    id: str
    created_at: datetime
    chunks: List[DocumentChunk] = []

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True
