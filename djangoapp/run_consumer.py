# NO LONGER USED BUT LEFT FOR REFERENCE
# NO LONGER USED BUT LEFT FOR REFERENCE

import logging
import os

import django

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

# NO LONGER USED BUT LEFT FOR REFERENCE
# NO LONGER USED BUT LEFT FOR REFERENCE
