from django.conf import settings
import httpx

# import requests
import logging

if settings.DEBUG:
    INFERENCE_SERVER_URL = "http://localhost:8099/predict"  # the dummy fastapi
else:
    INFERENCE_SERVER_URL = (
        "http://inferenceapp:8099/predict"  # the dummy fastapi server
    )

print(INFERENCE_SERVER_URL)


def run_inference(image_path):
    # with open(image_path, "rb") as img:
    #     files = {"file": img}
    #     encoded_path = urllib.parse.quote(image_path)
    #     data = {"path": encoded_path}
    #     response = requests.post(INFERENCE_SERVER_URL, files=files, data=data)
    with open(image_path, "rb") as img:
        files = {"file": img}
        data = {"path": image_path}
        with httpx.Client() as client:
            response = client.post(INFERENCE_SERVER_URL, files=files, data=data)
            logging.info(response.json())

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Inference failed with status code {response.status_code}")
