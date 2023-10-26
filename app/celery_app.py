import os
import ffmpeg
from celery import Celery
from app.crud import update_task_status
from app.database import SessionLocal
from app.models import TaskStatus

celery_app = Celery(
    "conversion_tool",
    broker="redis://default:strong-password@34.171.232.213:6379/0",
    backend="redis://default:strong-password@34.171.232.213:6379/0",
)


@celery_app.task(name="app.workers.convert_file")
def convert_file(task_id: int, original_format: str, target_format: str):
    db = SessionLocal()

    base_dir = os.path.join(os.getcwd(), "files")
    original_dir = os.path.join(base_dir, "original")
    converted_dir = os.path.join(base_dir, "converted")

    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(converted_dir, exist_ok=True)

    input_path = os.path.join(original_dir, f"{task_id}.{original_format}")
    output_path = os.path.join(converted_dir, f"{task_id}.{target_format}")

    try:
        ffmpeg.input(input_path).output(output_path).run()
        update_task_status(db, task_id, TaskStatus.PROCESSED)
    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        update_task_status(db, task_id, TaskStatus.ERROR)
    finally:
        db.close()
