import requests
from django.conf import settings

if settings.DEBUG:
    INFERENCE_SERVER_URL = "http://localhost:8000/predict"  # the dummy fastapi
else:
    INFERENCE_SERVER_URL = "http://inferenceapp:8099/predict"  # the dummy fastapi server


def run_inference(image_path):
    with open(image_path, "rb") as img:
        files = {"file": img}
        response = requests.post(INFERENCE_SERVER_URL, files=files)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Inference failed with status code {response.status_code}")
