from datetime import datetime
from typing import Optional
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from core.security import verify_password, get_password_hash
from db.models.user import User
from fastapi import HTTPException, status
from db.models.task import Task


def create_user(db: Session, username: str, email: str, password: str):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_credentials(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def get_user_tasks(
    db: Session, user_id: int, max: Optional[int] = 10, order: Optional[int] = 0
):
    if order == 0:
        tasks = (
            db.query(Task)
            .filter(Task.user_id == user_id)
            .order_by(asc(Task.id))
            .limit(max)
            .all()
        )
    else:
        tasks = (
            db.query(Task)
            .filter(Task.user_id == user_id)
            .order_by(desc(Task.id))
            .limit(max)
            .all()
        )
    return tasks


def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_task(db: Session, file_name: str, new_format: str, user_id: int):
    db_task = Task(
        original_format=file_name.split(".")[-1],
        target_format=new_format,
        user_id=user_id,
        status="uploaded",
        created_at=datetime.utcnow(),
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()
