from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from ..database import get_db
from ..models.chat import ChatSession, ChatMessage
from ..models.ticket import Ticket
from ..schemas.ticket import TicketResponse, TicketEscalateRequest, TicketUpdateStatus, TicketAssign
from ..services.ticket_service import ticket_classifier
from .chat import analyze_sentiment_heuristic

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"]
)

@router.post("/escalate", response_model=TicketResponse)
def escalate_session(payload: TicketEscalateRequest, db: Session = Depends(get_db)):
    """
    Escalates an active chat session to a support ticket:
    1. Collects chat session context.
    2. Runs ML classifier on the description to predict category and priority.
    3. Persists the support ticket in SQL.
    4. Updates chat session status to "escalated".
    """
    # 1. Verify session exists
    session = db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")
        
    if session.status == "escalated":
        # Check if ticket already exists
        existing_ticket = db.query(Ticket).filter(Ticket.session_id == payload.session_id).first()
        if existing_ticket:
            return existing_ticket
    
    # Calculate sentiment of the escalation description
    sentiment = analyze_sentiment_heuristic(payload.description)
    
    # 2. Run ML classification on the description text
    predicted_category = ticket_classifier.predict_category(payload.description)
    predicted_priority = ticket_classifier.predict_priority(payload.description, sentiment)
    
    # 3. Create Ticket record
    ticket = Ticket(
        session_id=payload.session_id,
        user_id=session.user_id,
        title=payload.title,
        description=payload.description,
        category=predicted_category,
        priority=predicted_priority,
        status="open"
    )
    
    # 4. Update Chat Session status
    session.status = "escalated"
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    return ticket

@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status: Optional[str] = None, 
    category: Optional[str] = None, 
    assigned_agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists all support tickets with filtering options."""
    query = db.query(Ticket)
    
    if status:
        query = query.filter(Ticket.status == status)
    if category:
        query = query.filter(Ticket.category == category)
    if assigned_agent_id:
        query = query.filter(Ticket.assigned_agent_id == assigned_agent_id)
        
    return query.order_by(Ticket.created_at.desc()).all()

@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(ticket_id: str, payload: TicketUpdateStatus, db: Session = Depends(get_db)):
    """Updates a ticket's status and logs resolved_at timestamp if resolved."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
        
    status_lower = payload.status.lower()
    if status_lower not in ["open", "in_progress", "resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status value.")
        
    ticket.status = status_lower
    
    if status_lower == "resolved":
        ticket.resolved_at = datetime.now(timezone.utc)
    else:
        ticket.resolved_at = None
        
    db.commit()
    db.refresh(ticket)
    return ticket

@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(ticket_id: str, payload: TicketAssign, db: Session = Depends(get_db)):
    """Assigns an agent to a ticket."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
        
    # Verify the assigned agent ID exists in database
    from ..models.user import User
    agent = db.query(User).filter(User.id == payload.assigned_agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Assigned agent user not found.")
        
    ticket.assigned_agent_id = payload.assigned_agent_id
    db.commit()
    db.refresh(ticket)
    return ticket
