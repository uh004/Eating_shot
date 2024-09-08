import os
import django
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("kafka").setLevel(logging.WARNING)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# Now you can import your Django models and use Django features
from ai_workload.kafka.consumer import start_consuming

if __name__ == "__main__":
    logging.info("Starting Kafka consumer...")
    start_consuming()
