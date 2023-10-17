import shutil
import os
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session
from app.celery_app import convert_file
from app.crud import create_task, delete_task, get_task, get_user_tasks
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import TaskList, TaskResponse

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


VALID_FORMATS = {"mp4", "webm", "avi"}


def validate_format(format: str) -> str:
    if format.lower() not in VALID_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format: {format}. Valid formats are: {', '.join(VALID_FORMATS)}.",
        )
    return format.lower()


@router.post("/api/tasks", response_model=dict)
async def create_task_endpoint(
    file: UploadFile = File(...),
    newFormat: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_format = file.filename.split(".")[-1].lower()
    validate_format(newFormat)
    validate_format(file_format)

    if file_format == newFormat.lower():
        raise HTTPException(
            status_code=400,
            detail="New format cannot be the same as the current format.",
        )

    task = create_task(db, file.filename, newFormat, current_user.id)
    file_location = os.path.join(
        os.getcwd(), "files", "original", f"{task.id}.{file_format}"
    )
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    convert_file.apply_async(args=[task.id, file_format, newFormat.lower()])

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


@router.delete("/api/tasks/{id_task}")
async def delete_task_endpoint(
    id_task: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, id_task)
    if task is None or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    delete_task(db, id_task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
