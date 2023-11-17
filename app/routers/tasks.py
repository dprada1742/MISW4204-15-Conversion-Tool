import json
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session
from app.crud import create_task, delete_task, get_task, get_user_tasks
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import TaskList, TaskResponse
from google.cloud import storage
from starlette.responses import StreamingResponse
from google.cloud import pubsub_v1

router = APIRouter()

storage_client = storage.Client()
bucket_name = "bucket-files"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("sw-nube-uniandes", "fastapi_conversion")


@router.get("/api/tasks", response_model=TaskList)
async def read_tasks(
    request: Request,
    max: int = Query(10, ge=1, le=100),
    order: int = Query(0, ge=0, le=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = get_user_tasks(request, db, user_id=current_user.id, max=max, order=order)
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

    file_path = f"original/{task.id}.{file_format}"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)

    try:
        blob.upload_from_file(file.file, content_type=file.content_type)
    except Exception as e:
        print(f"Error while uploading file: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error while uploading file.",
        )

    message_data = {
        "task_id": task.id,
        "original_format": file_format,
        "target_format": newFormat.lower(),
    }
    publisher.publish(topic_path, json.dumps(message_data).encode("utf-8"))

    return {"message": "Task created successfully"}


@router.get("/api/tasks/{id_task}", response_model=TaskResponse)
async def get_task_endpoint(
    request: Request,
    id_task: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, id_task)
    if task is None or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    base_url = request.base_url.scheme + "://" + request.base_url.netloc
    original_file_url = f"{base_url}/files/original/{task.id}.{task.original_format}"
    processed_file_url = f"{base_url}/files/converted/{task.id}.{task.target_format}"

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


@router.get("/files/original/{task_id}.{original_format}")
async def serve_original_file(
    task_id: int = Path(..., title="The ID of the task"),
    original_format: str = Path(..., title="The original format of the file"),
):
    file_path = f"original/{task_id}.{original_format}"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)

    if not blob.exists():
        raise HTTPException(status_code=404, detail="File not found")

    response = StreamingResponse(blob.open("rb"), media_type="application/octet-stream")
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename={task_id}.{original_format}"

    return response


@router.get("/files/converted/{task_id}.{target_format}")
async def serve_converted_file(
    task_id: int = Path(..., title="The ID of the task"),
    target_format: str = Path(..., title="The target format of the file"),
):
    file_path = f"converted/{task_id}.{target_format}"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)

    if not blob.exists():
        raise HTTPException(status_code=404, detail="File not found")

    response = StreamingResponse(blob.open("rb"), media_type="application/octet-stream")
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename={task_id}.{target_format}"

    return response
