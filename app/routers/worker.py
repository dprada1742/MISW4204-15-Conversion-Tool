import os
import json
import ffmpeg
from google.cloud import storage
from app.crud import update_task_status
from app.database import SessionLocal
from app.models import TaskStatus
import tempfile
import traceback
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

storage_client = storage.Client()
bucket_name = "bucket-uniandes"
bucket = storage_client.get_bucket(bucket_name)


def convert_file_logic(task_id, original_format, target_format):
    db = SessionLocal()
    try:
        original_blob = bucket.blob(f"original/{task_id}.{original_format}")
        converted_blob = bucket.blob(f"converted/{task_id}.{target_format}")

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, f"{task_id}.{original_format}")
            output_path = os.path.join(temp_dir, f"{task_id}.{target_format}")
            original_blob.download_to_filename(input_path)

            try:
                ffmpeg.input(input_path).output(output_path).run()
                converted_blob.upload_from_filename(output_path)
                update_task_status(db, task_id, TaskStatus.PROCESSED)
            except Exception as e:
                print(
                    f"Error occurred during file conversion for task ID {task_id}: {e}"
                )
                traceback.print_exc()
                update_task_status(db, task_id, TaskStatus.ERROR)
    finally:
        db.close()


@router.post("/api/worker")
async def pubsub_push(request: Request):
    envelope = await request.json()

    if "message" not in envelope:
        raise HTTPException(status_code=400, detail="Invalid Pub/Sub message format")

    message = envelope["message"]

    if "data" not in message:
        raise HTTPException(status_code=400, detail="No data in Pub/Sub message")

    message_data = json.loads(message["data"].decode("utf-8"))

    convert_file_logic(
        message_data["task_id"],
        message_data["original_format"],
        message_data["target_format"],
    )

    return {"status": "Processed message"}
