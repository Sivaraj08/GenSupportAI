import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="SET NULL"), unique=True, nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    priority = Column(String(50), nullable=False, default="medium") # low, medium, high, critical
    category = Column(String(50), nullable=False, default="general") # billing, technical, sales, general
    status = Column(String(50), nullable=False, default="open") # open, in_progress, resolved
    
    assigned_agent_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    session = relationship("ChatSession", back_populates="ticket")
    
    # Define primaryjoin to disambiguate between creator user and assigned agent user
    user = relationship("User", foreign_keys=[user_id])
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id])
