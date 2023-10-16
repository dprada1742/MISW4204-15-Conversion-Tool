from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional


class SignUpRequest(BaseModel):
    username: str
    password1: str
    password2: str
    email: EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class TaskBase(BaseModel):
    original_format: str
    target_format: str
    status: Optional[str]


class TaskInDB(TaskBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True


class TaskList(BaseModel):
    tasks: List[TaskInDB]
