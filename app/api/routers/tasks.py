from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session
from api.dependencies import get_current_user
from api.schemas import TaskList
from db.session import get_db
from db.crud import create_task, get_user_tasks
from db.models.user import User

router = APIRouter()


@router.get("/api/tasks", response_model=TaskList)
async def read_tasks(
    max: int = Query(10, ge=1, le=100),
    order: int = Query(0, ge=0, le=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = get_user_tasks(db, user_id=current_user.id, max=max, order=order)
    return {"tasks": tasks}


@router.post("/api/tasks", response_model=dict)
async def create_task_endpoint(
    file: UploadFile = File(...),
    newFormat: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = create_task(db, file.filename, newFormat, current_user.id)
    return {"message": "Task created successfully"}
