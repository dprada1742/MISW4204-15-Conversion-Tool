from fastapi import UploadFile
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List
from db.models.task import TaskStatus


class SignUpRequest(BaseModel):
    username: str
    password1: str
    password2: str
    email: EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class TaskResponse(BaseModel):
    id: int
    original_format: str
    target_format: str
    status: TaskStatus
    created_at: datetime
    original_file_url: str
    processed_file_url: str


class TaskList(BaseModel):
    tasks: List[TaskResponse]


class CreateTaskRequest(BaseModel):
    fileName: UploadFile
    newFormat: str
