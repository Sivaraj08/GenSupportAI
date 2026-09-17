import os
import sys

# Adjust Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force SQLite if PostgreSQL is not available
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///./gensupport.db"

# Force LLM model to be llama3.2:latest since it's the one installed on Ollama
os.environ["LLM_MODEL"] = "llama3.2:latest"

from app.database import engine, SessionLocal
from app.models.document import Document
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service

def test_queries():
    db = SessionLocal()
    
    # 1. Print registered documents
    print("=== Registered Documents in Database ===")
    docs = db.query(Document).all()
    for doc in docs:
        print(f"ID: {doc.id} | Filename: {doc.filename} | Status: {doc.status} | Chunks: {doc.chunk_count}")
    
    # 2. Define test questions
    queries = [
        "What are the eligibility criteria for BE Computer Science?",
        "How much is the hostel fee for an AC room?",
        "What documents do I need to bring for admission?",
        "Tell me about the first graduate scholarship."
    ]
    
    # 3. Query RAG and LLM
    for q in queries:
        print(f"\n==========================================")
        print(f"Question: {q}")
        print(f"==========================================")
        
        # Get chunks
        retrieved_chunks = rag_service.query_similarity(q, top_k=3)
        print(f"\n[RAG] Retrieved {len(retrieved_chunks)} relevant chunks:")
        for idx, chunk in enumerate(retrieved_chunks):
            filename = chunk['metadata'].get('filename', 'Unknown')
            page = chunk['metadata'].get('page_num', 'Unknown')
            print(f"  - Chunk {idx+1} (Source: {filename}, Page: {page}):")
            snippet = chunk['text']
            print(f"    \"{snippet[:200]}...\"")
            
        # Call LLM
        print("\n[LLM] Generating answer using Ollama...")
        response = llm_service.generate_response(
            context_chunks=retrieved_chunks,
            history=[],
            query=q
        )
        print(f"\nResponse:\n{response}")
        print(f"==========================================\n")
        
    db.close()

if __name__ == "__main__":
    test_queries()
