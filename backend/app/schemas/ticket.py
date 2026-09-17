from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TicketBase(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    category: str = "general"
    status: str = "open"
    assigned_agent_id: Optional[str] = None

class TicketCreate(TicketBase):
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class TicketUpdateStatus(BaseModel):
    status: str

class TicketAssign(BaseModel):
    assigned_agent_id: str

class TicketResponse(TicketBase):
    id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TicketEscalateRequest(BaseModel):
    session_id: str
    title: str
    description: str
