import uuid
from sqlalchemy import Column, String
from ..database import Base

class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    department = Column(String(50), nullable=False)  # cse, it, aids
    course_code = Column(String(50), nullable=False)
    course_name = Column(String(100), nullable=False)
    exam_date = Column(String(50), nullable=False)
    exam_session = Column(String(50), nullable=False)  # FN, AN
