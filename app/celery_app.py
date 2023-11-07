import os
import ffmpeg
from celery import Celery
from app.crud import update_task_status
from app.database import SessionLocal
from app.models import TaskStatus
from google.cloud import storage
import tempfile

celery_app = Celery(
    "conversion_tool",
    broker="redis://default:strong-password@10.128.0.5:6379/0",
    backend="redis://default:strong-password@10.128.0.5:6379/0",
)

# Initialize the GCP storage client
storage_client = storage.Client()
bucket_name = "bucket-files"
bucket = storage_client.get_bucket(bucket_name)


@celery_app.task(name="app.workers.convert_file")
def convert_file(task_id: int, original_format: str, target_format: str):
    db = SessionLocal()

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
            error_message = str(e)
            print(f"Error: {error_message}")
            update_task_status(db, task_id, TaskStatus.ERROR)
        finally:
            db.close()
