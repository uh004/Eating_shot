from kafka import KafkaProducer
import json

from core import settings

producer = KafkaProducer(
    bootstrap_servers=[settings.KAFKA_BOOTSTRAP_SERVERS],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def send_inference_task(task_id):
    producer.send("inference_tasks", {"task_id": task_id})
