from .models import InferenceTask, InferenceResult
from .inference_client import run_inference


# TODO: any better way other than this??
# TODO: stress test on this?
def process_inference_task(task_id):
    task = InferenceTask.objects.get(id=task_id)
    task.status = "PROCESSING"
    task.save()

    try:
        result_data = run_inference(task.photo.path)
        result = InferenceResult.objects.create(result_data=result_data)
        task.result = result
        task.status = "COMPLETED"
    except Exception:
        task.status = "FAILED"
    finally:
        task.save()
