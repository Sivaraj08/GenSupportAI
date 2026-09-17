    import os
    import sys
    from unittest.mock import patch

    # Adjust Python path to import app correctly
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    from app.database import engine, Base, SessionLocal
    from app.models.document import Document, DocumentChunk
    from app.services.rag_service import rag_service

    def run_test():
        print("Initializing test database tables...")
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        
        # Clean database before testing
        db.query(DocumentChunk).delete()
        db.query(Document).delete()
        db.commit()
        
        # Initialize mock document metadata
        doc_id = "test-document-uuid-12345"
        filename = "test_manual.pdf"
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
        
        # Mock data to return from PDF extraction
        mock_extracted_pages = [
            {
                "page_num": 1,
                "text": (
                    "GenSupportAI is an Enterprise AI Customer Support Knowledge Assistant. "
                    "It combines RAG Knowledge Retrieval, Generative AI Chatbot Assistant, "
                    "Smart Ticket Management, and Predictive Analytics to form a closed-loop customer support cycle. "
                    "Phase 1 implements document parsing, chunk splitting, embedding extraction, and similarity index."
                )
            },
            {
                "page_num": 2,
                "text": (
                    "For database administration: To reboot the primary SQL database cluster, operators must run "
                    "'sudo systemctl restart postgresql' on the host system. Always monitor the active connection pool "
                    "and ensure all client transactions are committed. In case of deadlocks, query PG_STAT_ACTIVITY to find blocked queries."
                )
            }
        ]
        
        print("Running ingestion with mocked PDF extraction...")
        # Patch the PDF extraction function to return our mock pages
        with patch.object(rag_service, "extract_text_from_pdf", return_value=mock_extracted_pages):
            success = rag_service.ingest_document(db, doc_id, file_path)
            
        if not success:
            print("ERROR: Ingestion failed.")
            sys.exit(1)
            
        # Refresh doc from database
        db.refresh(db_doc)
        print(f"Ingestion successful!")
        print(f"Document Status: {db_doc.status}")
        print(f"Chunks Count: {db_doc.chunk_count}")
        
        # Check relational chunks
        db_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).all()
        print(f"Stored chunks in Database: {len(db_chunks)}")
        for i, chunk in enumerate(db_chunks):
            print(f" - Chunk {i+1}: Length {len(chunk.content)} chars, Vector Ref ID: {chunk.vector_ref}")
            
        # Test Similarity Search
        query = "How do I reboot the SQL database cluster?"
        print(f"\nTesting Vector Similarity Search for query: '{query}'")
        results = rag_service.query_similarity(query, top_k=2)
        
        print(f"Found {len(results)} matching results:")
        for idx, match in enumerate(results):
            print(f"\n[Result {idx+1}] Match ID: {match['id']}")
            print(f"Distance (Cosine): {match['distance']:.4f}")
            print(f"Source Page: {match['metadata']['page_num']}")
            print(f"Content: {match['text']}")

        # Clean up test database records
        print("\nCleaning up test assets...")
        rag_service.delete_document_vectors(doc_id)
        db.delete(db_doc)
        db.commit()
        print("Cleanup completed.")
        db.close()
        
        print("\n--- Phase 1 Verification Test Passed Successfully! ---")

    if __name__ == "__main__":
        run_test()
