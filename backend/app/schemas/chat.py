from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Any

# User schemas
class UserBase(BaseModel):
    name: str
    email: str
    role: str = "customer"

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Chat Message schemas
class ChatMessageBase(BaseModel):
    sender: str # user, assistant
    content: str
    retrieved_chunks: Optional[List[Any]] = []
    sentiment: Optional[str] = None

class ChatMessageCreate(ChatMessageBase):
    session_id: str

class ChatMessageResponse(ChatMessageBase):
    id: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Chat Session schemas
class ChatSessionBase(BaseModel):
    user_id: Optional[str] = None
    status: str = "active"
    title: Optional[str] = None

class ChatSessionCreate(BaseModel):
    user_id: Optional[str] = None

class ChatSessionResponse(ChatSessionBase):
    id: str
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True

# Payload schemas
class ChatMessageRequest(BaseModel):
    session_id: str
    content: str
