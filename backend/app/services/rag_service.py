import os
import uuid
import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from ..config import settings
from ..models.document import Document, DocumentChunk
from sqlalchemy.orm import Session

class RAGService:
    def __init__(self):
        self._embedding_model = None
        self._chroma_client = None
        self._collection = None

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            # Load the sentence transformer model lazily
            print(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}...")
            self._embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            print("Embedding model loaded successfully.")
        return self._embedding_model

    @property
    def chroma_collection(self):
        if self._chroma_client is None:
            self._chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
            self._collection = self._chroma_client.get_or_create_collection(
                name="document_collection",
                metadata={"hnsw:space": "cosine"} # cosine similarity metric
            )
        return self._collection

    def extract_text_from_pdf(self, pdf_path: str) -> list:
        """
        Extracts raw text from a PDF document page by page.
        Returns a list of dicts: [{'page_num': int, 'text': str}]
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")

        reader = PdfReader(pdf_path)
        pages_data = []
        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                pages_data.append({
                    "page_num": page_idx + 1,
                    "text": text
                })
        return pages_data

    def extract_text_from_csv(self, csv_path: str) -> list:
        """
        Extracts raw text from a CSV spreadsheet row by row.
        Returns a list of dicts: [{'page_num': int, 'text': str}]
        where page_num corresponds to the row number.
        """
        import csv
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at {csv_path}")

        rows_data = []
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if not headers:
                return []
            
            headers = [h.strip() for h in headers]
            
            for idx, row in enumerate(reader):
                if not row or not any(cell.strip() for cell in row):
                    continue
                
                parts = []
                q_idx = -1
                a_idx = -1
                for i, h in enumerate(headers):
                    h_lower = h.lower()
                    if 'question' in h_lower or 'query' in h_lower:
                        q_idx = i
                    elif 'answer' in h_lower or 'response' in h_lower or 'info' in h_lower or 'syllabus' in h_lower:
                        a_idx = i
                
                if q_idx != -1 and a_idx != -1 and q_idx < len(row) and a_idx < len(row):
                    question = row[q_idx].strip()
                    answer = row[a_idx].strip()
                    parts.append(f"Question: {question}")
                    parts.append(f"Answer: {answer}")
                    
                    for i, val in enumerate(row):
                        if i != q_idx and i != a_idx and i < len(headers) and i < len(row):
                            val_str = val.strip()
                            if val_str:
                                parts.append(f"{headers[i]}: {val_str}")
                else:
                    for i, val in enumerate(row):
                        if i < len(headers) and i < len(row):
                            val_str = row[i].strip()
                            if val_str:
                                parts.append(f"{headers[i]}: {val_str}")
                
                row_text = "\n".join(parts)
                if row_text.strip():
                    rows_data.append({
                        "page_num": idx + 2, # row numbers start after header
                        "text": row_text
                    })
        return rows_data

    def extract_text_from_excel(self, excel_path: str) -> list:
        """
        Extracts raw text from an Excel spreadsheet (.xlsx, .xls) row by row.
        Returns a list of dicts: [{'page_num': int, 'text': str}]
        where page_num corresponds to the row number.
        """
        import openpyxl
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel file not found at {excel_path}")

        wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
        rows_data = []
        sheet = wb.active
        
        rows_iter = sheet.iter_rows(values_only=True)
        headers = next(rows_iter, None)
        if not headers:
            return []
        
        headers = [str(h).strip() if h is not None else f"Column_{i}" for i, h in enumerate(headers)]
        
        for idx, row in enumerate(rows_iter):
            if not row or not any(cell is not None and str(cell).strip() for cell in row):
                continue
            
            parts = []
            q_idx = -1
            a_idx = -1
            for i, h in enumerate(headers):
                h_lower = h.lower()
                if 'question' in h_lower or 'query' in h_lower:
                    q_idx = i
                elif 'answer' in h_lower or 'response' in h_lower or 'info' in h_lower or 'syllabus' in h_lower:
                    a_idx = i
                    
            if q_idx != -1 and a_idx != -1 and q_idx < len(row) and a_idx < len(row):
                question = str(row[q_idx]).strip() if row[q_idx] is not None else ""
                answer = str(row[a_idx]).strip() if row[a_idx] is not None else ""
                parts.append(f"Question: {question}")
                parts.append(f"Answer: {answer}")
                
                for i, val in enumerate(row):
                    if i != q_idx and i != a_idx and i < len(headers) and i < len(row):
                        val_str = str(val).strip() if val is not None else ""
                        if val_str:
                            parts.append(f"{headers[i]}: {val_str}")
            else:
                for i, val in enumerate(row):
                    if i < len(headers) and i < len(row):
                        val_str = str(val).strip() if val is not None else ""
                        if val_str:
                            parts.append(f"{headers[i]}: {val_str}")
                            
            row_text = "\n".join(parts)
            if row_text.strip():
                rows_data.append({
                    "page_num": idx + 2, # row numbers start after header
                    "text": row_text
                })
        return rows_data


    def split_text_into_chunks(self, pages_data: list, chunk_size: int = 800, overlap: int = 150) -> list:
        """
        Splits extracted pages text into chunks while preserving paragraph integrity where possible.
        """
        chunks = []
        for page in pages_data:
            text = page["text"]
            page_num = page["page_num"]
            
            start = 0
            text_len = len(text)
            
            while start < text_len:
                end = min(start + chunk_size, text_len)
                
                # If we're not at the very end of the page text, search backwards for clean splitting boundaries
                if end < text_len:
                    # Look back in the window to find logical break characters
                    search_window = text[max(start, end - 150):end]
                    found_boundary = -1
                    
                    for sep in ["\n\n", "\n", " ", ""]:
                        if not sep:
                            continue
                        idx = search_window.rfind(sep)
                        if idx != -1:
                            found_boundary = max(start, end - 150) + idx + len(sep)
                            break
                    
                    if found_boundary != -1:
                        end = found_boundary
                
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "text": chunk_text,
                        "page_num": page_num
                    })
                
                # Setup next chunk start index incorporating the overlap
                start = end - overlap
                if start >= text_len or end == text_len:
                    break
        return chunks

    def ingest_document(self, db: Session, document_id: str, file_path: str) -> bool:
        """
        Executes the full RAG pipeline:
        1. Extract text
        2. Chunk text
        3. Embed chunks
        4. Store embeddings in ChromaDB
        5. Store metadata in PostgreSQL/SQLite DB
        6. Update document state
        """
        db_doc = db.query(Document).filter(Document.id == document_id).first()
        if not db_doc:
            print(f"Document ID {document_id} not found in database.")
            return False

        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # 1. Extract & Chunk depending on format
            if file_ext == ".pdf":
                pages_data = self.extract_text_from_pdf(file_path)
                if not pages_data:
                    raise ValueError("No extractable text found in the PDF.")
                chunks_data = self.split_text_into_chunks(
                    pages_data, 
                    chunk_size=settings.CHUNK_SIZE, 
                    overlap=settings.CHUNK_OVERLAP
                )
            elif file_ext in [".xlsx", ".xls"]:
                pages_data = self.extract_text_from_excel(file_path)
                if not pages_data:
                    raise ValueError("No extractable rows found in the Excel file.")
                chunks_data = [{"text": r["text"], "page_num": r["page_num"]} for r in pages_data]
            elif file_ext == ".csv":
                pages_data = self.extract_text_from_csv(file_path)
                if not pages_data:
                    raise ValueError("No extractable rows found in the CSV file.")
                chunks_data = [{"text": r["text"], "page_num": r["page_num"]} for r in pages_data]
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            if not chunks_data:
                raise ValueError("No text chunks generated.")

            # 3. Vectorize and Store
            ids = []
            documents_texts = []
            metadatas = []
            db_chunks = []

            for idx, chunk in enumerate(chunks_data):
                vector_id = str(uuid.uuid4())
                ids.append(vector_id)
                documents_texts.append(chunk["text"])
                metadatas.append({
                    "document_id": document_id,
                    "filename": db_doc.filename,
                    "page_num": chunk["page_num"]
                })
                
                # Prepare relational SQL record
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk["text"],
                    vector_ref=vector_id
                )
                db_chunks.append(db_chunk)

            # Compute embeddings in bulk
            embeddings = self.embedding_model.encode(documents_texts).tolist()

            # Store to Vector DB (ChromaDB)
            collection = self.chroma_collection
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents_texts,
                metadatas=metadatas
            )

            # Store references to Relational DB
            db.add_all(db_chunks)
            db_doc.status = "indexed"
            db_doc.chunk_count = len(db_chunks)
            db.commit()
            
            print(f"Successfully indexed document {db_doc.filename}. Generated {len(db_chunks)} chunks.")
            return True

        except Exception as e:
            db.rollback()
            db_doc.status = "failed"
            db.commit()
            print(f"Failed to ingest document {db_doc.filename}: {str(e)}")
            return False

    def query_similarity(self, query: str, top_k: int = 3) -> list:
        """
        Executes a vector search in ChromaDB.
        Returns matching chunks with text, distance metrics, and metadata sources.
        """
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        collection = self.chroma_collection
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            ids = results["ids"][0]
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            
            for i in range(len(docs)):
                formatted_results.append({
                    "id": ids[i],
                    "text": docs[i],
                    "metadata": metas[i] if metas[i] is not None else {},
                    "distance": distances[i]
                })
        
        return formatted_results

    def delete_document_vectors(self, document_id: str) -> bool:
        """
        Removes all vectors belonging to a document from ChromaDB.
        """
        try:
            collection = self.chroma_collection
            collection.delete(where={"document_id": document_id})
            return True
        except Exception as e:
            print(f"Error deleting vectors for doc {document_id}: {str(e)}")
            return False

rag_service = RAGService()
