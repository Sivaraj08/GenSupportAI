import uuid
from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), nullable=False, default="customer") # admin, agent, customer
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
