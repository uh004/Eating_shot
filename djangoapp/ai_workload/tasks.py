from users.models import Diet
from .models import InferenceTask, InferenceResult
from .inference_client import run_inference
from celery import shared_task


# TODO: any better way other than this??
# TODO: stress test on this?


# this is run by the consumer. refresh the consumer if any changes are made
# def process_inference_task(task_id):
@shared_task(queue="ai_queue")
def process_inference_task(task_id):
    task = InferenceTask.objects.get(id=task_id)
    task.status = "PROCESSING"
    task.save()

    try:
        result_data = run_inference(task.photo.path)
        """
        [{"name": "\ub3c4\ud1a0\ub9ac\ubb35", "class": 1, "confidence": 0.47512, "box": {"x1": 87.85016, "y1": 87.95764, "x2": 301.8219, "y2": 288.64481}}, {"name": "\ub5a1\uac08\ube44", "class": 2, "confidence": 0.26878, "box": {"x1": 331.60638, "y1": 56.98588, "x2": 578.69916, "y2": 358.71658}}]
        """
        result_names_comma_separated = ",".join(
            [result["name"] for result in result_data]
        )
        result = InferenceResult.objects.create(
            result_data=result_data,
            result_names_comma_separated=result_names_comma_separated,
        )

        diet = Diet.objects.get(image=task.photo)
        diet.result_id = task_id
        diet.save()
        task.result = result
        task.status = "COMPLETED"
    except Exception as e:
        print(e)
        task.status = "FAILED"
    finally:
        task.save()
