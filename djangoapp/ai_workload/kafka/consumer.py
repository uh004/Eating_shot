from kafka import KafkaConsumer
import json

from core import settings
from ..tasks import process_inference_task

consumer = KafkaConsumer(
    "inference_tasks",
    group_id="ai_workload",
    bootstrap_servers=[settings.KAFKA_BOOTSTRAP_SERVERS],
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest",
)


# this is run by external script. so no lazy loading here
def start_consuming():
    for message in consumer:
        print(
            f"Received message: {message.value} from topic: {message.topic} partition: {message.partition} offset: {message.offset}"
        )
        process_inference_task(message.value["task_id"])
        # what if the database is down?
