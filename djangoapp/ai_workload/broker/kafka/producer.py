from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from core import settings

logger = logging.getLogger(__name__)

class LazyKafkaProducer:
    def __init__(self):
        self._producer = None

    def _get_producer(self):
        if self._producer is None:
            try:
                self._producer = KafkaProducer(
                    bootstrap_servers=[settings.KAFKA_BOOTSTRAP_SERVERS],
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
            except KafkaError as e:
                logger.error(f"Failed to connect to Kafka: {e}")
                self._producer = None
        return self._producer

    def send_inference_task(self, task_id):
        producer = self._get_producer()
        if producer:
            try:
                producer.send("inference_tasks", {"task_id": task_id})
            except KafkaError as e:
                logger.error(f"Failed to send message to Kafka: {e}")
        else:
            logger.warning(f"Kafka producer not available. Task {task_id} not sent.")

lazy_producer = LazyKafkaProducer()

def send_inference_task(task_id):
    lazy_producer.send_inference_task(task_id)
