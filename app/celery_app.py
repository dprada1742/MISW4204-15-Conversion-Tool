from celery import Celery

celery_app = Celery(
    "conversion_tool",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)


@celery_app.task(name="app.workers.convert_file")
def convert_file(task_id: int, original_format: str, target_format: str):
    print("File convertion task called")
    pass
