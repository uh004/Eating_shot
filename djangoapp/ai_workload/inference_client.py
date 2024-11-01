# import requests
import logging

import httpx
from core.settings import INFERENCE_SERVER_URL

timeout = httpx.Timeout(connect=30.0, read=30.0, write=30.0, pool=30.0)


def run_inference(image_path):
    print(INFERENCE_SERVER_URL)

    # with open(image_path, "rb") as img:
    #     files = {"file": img}
    #     encoded_path = urllib.parse.quote(image_path)
    #     data = {"path": encoded_path}
    #     response = requests.post(INFERENCE_SERVER_URL, files=files, data=data)
    with open(image_path, "rb") as img:
        files = {"file": img}
        data = {"path": image_path}
        with httpx.Client() as client:
            response = client.post(
                f"{INFERENCE_SERVER_URL}/predict",
                files=files,
                data=data,
                timeout=timeout,
            )
            logging.info(response.json())

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Inference failed with status code {response.status_code}")
