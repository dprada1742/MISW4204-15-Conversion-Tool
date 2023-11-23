from google.cloud import pubsub_v1
import json
import datetime

current_datetime = datetime.datetime.now()
print(f"Script executed at: {current_datetime}")


def publish_messages(project_id, topic_id, n):
    """Publishes multiple messages to a Pub/Sub topic."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    for i in range(n):
        message_data = {
            "task_id": 28992,
            "original_format": "avi",
            "target_format": "webm",
        }

        message_json = json.dumps(message_data)
        message_bytes = message_json.encode("utf-8")
        future = publisher.publish(topic_path, data=message_bytes)
        print(f"Published message {i + 1} to {topic_path}: {future.result()}")


if __name__ == "__main__":
    project_id = "sw-nube-uniandes"
    topic_id = "fastapi_conversion"
    n = 1

    publish_messages(project_id, topic_id, n)
