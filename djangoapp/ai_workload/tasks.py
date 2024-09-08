from users.models import Diet
from .models import InferenceTask, InferenceResult
from .inference_client import run_inference


# TODO: any better way other than this??
# TODO: stress test on this?
# this is run by the consumer. refresh the consumer if any changes are made
def process_inference_task(task_id):
    task = InferenceTask.objects.get(id=task_id)
    task.status = "PROCESSING"
    task.save()

    try:
        result_data = run_inference(task.photo.path)
        result = InferenceResult.objects.create(result_data=result_data)

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
