from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.chat import ChatSession, ChatMessage
from ..models.exam_schedule import ExamSchedule
from ..models.document import Document
from ..models.user import User
from ..schemas.chat import ChatSessionResponse, ChatMessageResponse, ChatMessageRequest, ChatSessionCreate
from ..services.rag_service import rag_service
from ..services.llm_service import llm_service

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

def analyze_sentiment_heuristic(text: str) -> str:
    """
    Simple keyword-based heuristic for message sentiment analysis.
    Will be expanded with ML models in Phase 4.
    """
    text_lower = text.lower()
    negatives = ["error", "bad", "worst", "fail", "broken", "unhappy", "angry", "terrible", "hate", "charge", "refund", "not working"]
    positives = ["great", "awesome", "solved", "fixed", "thank", "helpful", "good", "love", "perfect", "resolved"]
    
    neg_count = sum(1 for word in negatives if word in text_lower)
    pos_count = sum(1 for word in positives if word in text_lower)
    
    if neg_count > pos_count:
        return "negative"
    elif pos_count > neg_count:
        return "positive"
    return "neutral"

@router.post("/session", response_model=ChatSessionResponse)
def create_session(session_data: ChatSessionCreate, db: Session = Depends(get_db)):
    """Starts a new chat session."""
    # Verify user exists if user_id is provided
    if session_data.user_id:
        user = db.query(User).filter(User.id == session_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
            
    session = ChatSession(
        user_id=session_data.user_id,
        status="active"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    """Retrieves all chat sessions ordered by creation time (newest first)."""
    return db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()


@router.get("/session/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """Retrieves all messages for a session in chronological order."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")
        
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()

@router.post("/message", response_model=ChatMessageResponse)
def send_message(payload: ChatMessageRequest, db: Session = Depends(get_db)):
    """
    Submits a user message:
    1. Persists user query.
    2. Performs RAG document retrieval.
    3. Retrieves past 5 message logs for history context.
    4. Generates an LLM response based on Ollama.
    5. Persists the AI response along with retrieved chunk sources.
    """
    # 1. Verify session exists
    session = db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    
    # 2. Persist User Message
    user_sentiment = analyze_sentiment_heuristic(payload.content)
    user_msg = ChatMessage(
        session_id=payload.session_id,
        sender="user",
        content=payload.content,
        sentiment=user_sentiment
    )
    db.add(user_msg)
    
    # Generate session title if it doesn't have one yet
    if not session.title:
        session.title = llm_service.generate_title(payload.content)
        
    db.commit()
    
    # 3. RAG Retrieval / Custom Exam Retrieval
    query_lower = payload.content.lower()
    has_exam_word = any(w in query_lower for w in ["exam", "exams", "examination", "examinations"])
    has_schedule_word = any(w in query_lower for w in ["timetable", "schedule", "date", "dates", "timing", "timings"])
    
    # Check if the last assistant response was the department prompt
    last_assistant_msg = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == payload.session_id, ChatMessage.sender == "assistant")\
        .order_by(ChatMessage.created_at.desc())\
        .first()
        
    is_replying_to_dept_prompt = False
    if last_assistant_msg and "Please let me know your department" in last_assistant_msg.content:
        is_replying_to_dept_prompt = True
        
    is_exam_query = (has_exam_word and has_schedule_word) or is_replying_to_dept_prompt
    
    if is_exam_query:
        # Determine department
        department = None
        if any(kw in query_lower for kw in ["cse", "computer science"]):
            department = "cse"
        elif any(kw in query_lower for kw in ["it", "information technology"]):
            department = "it"
        elif any(kw in query_lower for kw in ["aids", "artificial intelligence", "ai & ds", "ai and ds"]):
            department = "aids"
            
        # Check history if not specified in the current query
        if not department:
            history_records = db.query(ChatMessage)\
                .filter(ChatMessage.session_id == payload.session_id)\
                .order_by(ChatMessage.created_at.desc())\
                .limit(5)\
                .all()
            for msg in history_records:
                msg_lower = msg.content.lower()
                if any(kw in msg_lower for kw in ["cse", "computer science"]):
                    department = "cse"
                    break
                elif any(kw in msg_lower for kw in ["it", "information technology"]):
                    department = "it"
                    break
                elif any(kw in msg_lower for kw in ["aids", "artificial intelligence", "ai & ds", "ai and ds"]):
                    department = "aids"
                    break
                    
        if department:
            # Fetch department exam timetable from Database
            schedules = db.query(ExamSchedule).filter(ExamSchedule.department == department).all()
            if schedules:
                schedule_lines = []
                for s in schedules:
                    schedule_lines.append(f"- Course Code: {s.course_code} | Course Name: {s.course_name} | Date: {s.exam_date} | Session: {s.exam_session}")
                formatted_schedule = f"Official Exam Timetable for Department {department.upper()}:\n" + "\n".join(schedule_lines)
                
                # Retrieve normal RAG context but prepend this specific exam timetable chunk
                retrieved_chunks = rag_service.query_similarity(payload.content, top_k=2)
                virtual_exam_chunk = {
                    "id": f"db_exam_schedule_{department}",
                    "text": formatted_schedule,
                    "metadata": {"page_num": "DB", "filename": f"{department.upper()} Exam Schedule"}
                }
                retrieved_chunks.insert(0, virtual_exam_chunk)
            else:
                retrieved_chunks = rag_service.query_similarity(payload.content, top_k=3)
        else:
            # Ask the user for their department
            ai_response_text = "Please let me know your department (CSE, IT, or AIDS) so I can fetch and display your exam timetable."
            ai_sentiment = "neutral"
            ai_msg = ChatMessage(
                session_id=payload.session_id,
                sender="assistant",
                content=ai_response_text,
                retrieved_chunks=[],
                sentiment=ai_sentiment
            )
            db.add(ai_msg)
            db.commit()
            db.refresh(ai_msg)
            return ai_msg
    else:
        # Standard RAG Retrieval
        retrieved_chunks = rag_service.query_similarity(payload.content, top_k=3)
    
    # Prepend list of all indexed documents in database as a virtual context chunk to help LLM recognize multiple candidates
    indexed_docs = db.query(Document).filter(Document.status == "indexed").all()
    if indexed_docs:
        doc_names = ", ".join([d.filename for d in indexed_docs])
        virtual_chunk = {
            "id": "virtual_doc_list",
            "text": f"List of uploaded resumes/candidate files in database: {doc_names}",
            "metadata": {"page_num": "DB", "filename": "Database"}
        }
        retrieved_chunks.insert(0, virtual_chunk)
    
    # 4. Load Conversation History
    history_records = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == payload.session_id)\
        .order_by(ChatMessage.created_at.asc())\
        .all()
    
    # Format history as a list of dicts for LLM Service
    history_list = [{"sender": msg.sender, "content": msg.content} for msg in history_records[:-1]] # exclude the current user message
    
    # 5. Generate LLM Response (Ollama)
    ai_response_text = llm_service.generate_response(
        context_chunks=retrieved_chunks,
        history=history_list,
        query=payload.content
    )
    
    # Format vector references for storage
    chunk_refs = [
        {
            "id": chunk["id"],
            "filename": chunk["metadata"].get("filename"),
            "page_num": chunk["metadata"].get("page_num"),
            "snippet": chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"]
        } for chunk in retrieved_chunks
    ]
    
    # 6. Persist AI Message
    ai_sentiment = analyze_sentiment_heuristic(ai_response_text)
    ai_msg = ChatMessage(
        session_id=payload.session_id,
        sender="assistant",
        content=ai_response_text,
        retrieved_chunks=chunk_refs,
        sentiment=ai_sentiment
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    
    return ai_msg
