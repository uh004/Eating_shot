from kafka import KafkaConsumer
import json

from core import settings
from ..tasks import process_inference_task

consumer = KafkaConsumer(
    "inference_tasks",
    bootstrap_servers=[settings.KAFKA_BOOTSTRAP_SERVERS],
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

# this is run by external script. so no lazy loading here
def start_consuming():
    for message in consumer:
        task_id = message.value["task_id"]
        process_inference_task(task_id)
