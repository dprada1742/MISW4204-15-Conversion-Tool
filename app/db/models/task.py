from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import relationship
from db.session import Base
from datetime import datetime


class TaskStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSED = "processed"
    ERROR = "error"


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tasks")
    original_format = Column(String, index=True)
    target_format = Column(String, index=True)
    status = Column(SQLAlchemyEnum(TaskStatus), index=True)
