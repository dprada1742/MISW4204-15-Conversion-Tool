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
from datetime import datetime
from database import Base


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


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    tasks = relationship("Task", back_populates="user")
