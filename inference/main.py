import io

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import UJSONResponse

# TODO: if we were hosting this on a separate server from django...

import uvicorn
import logging
import logstash

import ultralytics
from ultralytics import YOLO
from PIL import Image

ultralytics.checks()

app = FastAPI(default_response_class=UJSONResponse)
host = "logstash"

logger = logging.getLogger("inference")
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler(host, 5000, version=1))

# change the fastapi app port
# uvicorn main:app --port 8000 --reload


## model loading
model = YOLO("models/food3.pt")
logging.info("Loaded the model.")


@app.get("/")
async def root():
    return {"message": str(model)}


@app.post("/predict")
async def inference_YOLO(file: UploadFile = File(...)):
    logger.info("Received inference request at /predict")
    # hardcoded conversion table
    conv_table = {
        "DotoriMook": "도토리묵",
        "KkakDugi": "깍두기",
        "TteokGalbi": "떡갈비",
        # ...
    }

    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    results = model.predict(source=image)
    logger.info([r.summary() for r in results])
    predictions = [r.summary() for r in results]
    for pred in predictions[0]:
        pred["name"] = conv_table.get(pred["name"], "아무렴뭐어때")

    return predictions[0]  # nested list. escape one level


if __name__ == "__main__":
    uvicorn.run(app, port=8099)
