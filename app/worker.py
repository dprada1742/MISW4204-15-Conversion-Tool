import os
import json
from exceptiongroup import catch
import ffmpeg
from google.cloud import pubsub_v1, storage
from app.crud import update_task_status
from app.database import SessionLocal
from app.models import TaskStatus
import tempfile

# Initialize the GCP storage client
storage_client = storage.Client()
bucket_name = "bucket-files"
bucket = storage_client.get_bucket(bucket_name)

# Pub/Sub Subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    "sw-nube-uniandes", "fastapi_subscriber"
)


def convert_file_logic(task_id, original_format, target_format):
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


def callback(message):
    print(f"Received message: {message.data.decode('utf-8')}")
    message_data = json.loads(message.data.decode("utf-8"))

    convert_file_logic(
        message_data["task_id"],
        message_data["original_format"],
        message_data["target_format"],
    )

    message.ack()


with subscriber:
    future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
