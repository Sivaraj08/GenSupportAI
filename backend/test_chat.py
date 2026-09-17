import os
import sys
from unittest.mock import patch

# Adjust Python path to import app correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.models.chat import ChatSession, ChatMessage
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service

def run_chat_test():
    print("Initializing test database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. Clean Database
    print("Cleaning database tables...")
    db.query(ChatMessage).delete()
    db.query(ChatSession).delete()
    db.query(User).delete()
    db.query(DocumentChunk).delete()
    db.query(Document).delete()
    db.commit()
    
    # 2. Create User
    print("Creating mock support agent...")
    mock_user = User(
        name="John Doe",
        email="john.doe@example.com",
        role="agent"
    )
    db.add(mock_user)
    db.commit()
    db.refresh(mock_user)
    print(f"Created Agent ID: {mock_user.id}")

    # 3. Seed Mock Knowledge Base
    print("\nSeeding database maintenance instructions into RAG index...")
    doc_id = "manual-doc-id-999"
    filename = "db_maintenance.pdf"
    file_path = os.path.join("./uploads", filename)
    
    db_doc = Document(
        id=doc_id,
        filename=filename,
        file_path=file_path,
        status="processing",
        chunk_count=0
    )
    db.add(db_doc)
    db.commit()
    
    mock_pdf_pages = [
        {
            "page_num": 1,
            "text": (
                "DATABASE CLUSTER MANUAL:\n"
                "To reboot the primary SQL database cluster, operators must execute: 'sudo systemctl restart postgresql' "
                "on the database server host. Operators must monitor active connection pools. "
                "Always verify that all client transactions are committed before initiating the reboot sequence. "
                "In case of deadlock errors, query the PG_STAT_ACTIVITY catalog table to find blocked backend process IDs."
            )
        }
    ]
    
    with patch.object(rag_service, "extract_text_from_pdf", return_value=mock_pdf_pages):
        rag_service.ingest_document(db, doc_id, file_path)
    
    db.refresh(db_doc)
    print(f"Indexed document status: {db_doc.status}, chunks: {db_doc.chunk_count}")

    # 4. Start Chat Session
    print("\nInitializing Chat Session...")
    session = ChatSession(
        user_id=mock_user.id,
        status="active"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    print(f"Session started ID: {session.id}")

    # 5. User Query 1 (RAG search lookup)
    query_1 = "How do I reboot the SQL database cluster?"
    print(f"\nUser: '{query_1}'")
    
    # Simulate API call POST /api/chat/message logic
    retrieved_chunks = rag_service.query_similarity(query_1, top_k=2)
    print(f"[RAG] Found {len(retrieved_chunks)} relevant documentation snippets.")
    
    # Persist user message
    user_msg_1 = ChatMessage(
        session_id=session.id,
        sender="user",
        content=query_1,
        sentiment="neutral"
    )
    db.add(user_msg_1)
    db.commit()
    
    # Generate LLM response
    print("[LLM] Querying local Ollama model (this may fall back if Ollama is offline)...")
    ai_reply_1 = llm_service.generate_response(
        context_chunks=retrieved_chunks,
        history=[],
        query=query_1
    )
    print(f"GenSupportAI: '{ai_reply_1}'")
    
    # Persist AI message
    ai_msg_1 = ChatMessage(
        session_id=session.id,
        sender="assistant",
        content=ai_reply_1,
        retrieved_chunks=[c["text"] for c in retrieved_chunks]
    )
    db.add(ai_msg_1)
    db.commit()

    # 6. User Query 2 (Follow-up to verify memory)
    query_2 = "What should I do in case of deadlocks?"
    print(f"\nUser: '{query_2}'")
    
    # Persist second user message
    user_msg_2 = ChatMessage(
        session_id=session.id,
        sender="user",
        content=query_2,
        sentiment="neutral"
    )
    db.add(user_msg_2)
    db.commit()
    
    # Retrieve similarity context
    retrieved_chunks_2 = rag_service.query_similarity(query_2, top_k=2)
    
    # Load recent session history
    history_records = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == session.id)\
        .order_by(ChatMessage.created_at.asc())\
        .all()
    
    # Format history context (excluding the current user message)
    history_list = [{"sender": msg.sender, "content": msg.content} for msg in history_records[:-1]]
    
    # Generate second response incorporating conversational memory
    ai_reply_2 = llm_service.generate_response(
        context_chunks=retrieved_chunks_2,
        history=history_list,
        query=query_2
    )
    print(f"GenSupportAI: '{ai_reply_2}'")
    
    # Persist second AI message
    ai_msg_2 = ChatMessage(
        session_id=session.id,
        sender="assistant",
        content=ai_reply_2,
        retrieved_chunks=[c["text"] for c in retrieved_chunks_2]
    )
    db.add(ai_msg_2)
    db.commit()

    # 7. Print Final Scroll History
    print("\n=== Chat Scroll History saved in database ===")
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == session.id)\
        .order_by(ChatMessage.created_at.asc())\
        .all()
    
    for msg in messages:
        sender_label = "User" if msg.sender == "user" else "Assistant"
        print(f"[{msg.created_at.strftime('%H:%M:%S')}] {sender_label}: {msg.content}")
        if msg.retrieved_chunks and msg.sender == "assistant":
            print(f"  [Sources]: {len(msg.retrieved_chunks)} document chunks referenced.")

    # 8. Cleanup test indexes
    print("\nCleaning up ChromaDB collections and DB tables...")
    rag_service.delete_document_vectors(doc_id)
    db.query(ChatMessage).delete()
    db.query(ChatSession).delete()
    db.query(User).delete()
    db.query(DocumentChunk).delete()
    db.query(Document).delete()
    db.commit()
    db.close()
    
    print("\n--- Phase 2 Conversational Assistant Verification Complete! ---")

if __name__ == "__main__":
    run_chat_test()
