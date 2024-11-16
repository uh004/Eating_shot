import logging

from celery import shared_task
from django.db import connection, transaction
from users.models import Diet

from .inference_client import run_inference
from .models import InferenceResult, InferenceTask

logger = logging.getLogger(__name__)


# TODO: any better way other than this??
# TODO: stress test on this?


# unused. for experimental purpose
def decrease_auto_increment(model):
    with connection.cursor() as cursor:
        table_name = model._meta.db_table
        cursor.execute(f"SELECT seq FROM sqlite_sequence WHERE name = '{table_name}';")
        current_value = cursor.fetchone()[0]
        new_value = max(0, current_value - 1)
        cursor.execute(
            f"UPDATE sqlite_sequence SET seq = {new_value} WHERE name = '{table_name}';"
        )


# this is run by the consumer. refresh the consumer if any changes are made
# def process_inference_task(task_id):
@shared_task(queue="ai_queue")
def process_inference_task(task_id):
    task = InferenceTask.objects.get(id=task_id)
    task.status = "PROCESSING"
    task.save()
    with transaction.atomic():
        try:
            result_data = run_inference(task.photo.path)
            logger.info("Inference completed successfully")

            result = InferenceResult.objects.create(result_data=result_data)
            logger.info("InferenceResult created successfully")

            diet = Diet.objects.get(image=task.photo)
            diet.result_id = result.id
            diet.save()
            logger.info("Diet updated successfully")

            task.result = result
            task.status = "COMPLETED"
            task.save()
            logger.info("Task completed successfully")

        except Exception as e:
            logger.error(f"Error occurred in task: {e}", exc_info=True)
            diet = Diet.objects.filter(image=task.photo).first()
            if diet:
                diet.delete()
                logger.info("Diet deleted successfully")
            task.status = "FAILED"
            task.save()
            logger.info("Task marked as FAILED")
        finally:
            task.save()
