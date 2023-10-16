from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from api.dependencies import get_current_user
from api.schemas import TaskList, TaskResponse
from db.session import get_db
from db.crud import create_task, get_task, get_user_tasks
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


@router.get("/api/tasks/{id_task}", response_model=TaskResponse)
async def get_task_endpoint(
    id_task: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, id_task)
    if task is None or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    original_file_url = f"/files/{task.id}/original.{task.original_format}"
    processed_file_url = f"/files/{task.id}/processed.{task.target_format}"

    return {
        "id": task.id,
        "original_format": task.original_format,
        "target_format": task.target_format,
        "status": task.status,
        "created_at": task.created_at,
        "original_file_url": original_file_url,
        "processed_file_url": processed_file_url,
    }
