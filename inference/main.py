from fastapi import FastAPI
import uvicorn
import logging
import logstash

# import ultralytics
# from ultralytics import YOLO

# ultralytics.checks()

app = FastAPI()
host = "logstash"

logger = logging.getLogger("inference")
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler(host, 5000, version=1))

# change the fastapi app port
# uvicorn main:app --port 8000 --reload


## model loading
# model = YOLO('<filename.pt>')

logging.info("Loaded the model.")


@app.get("/")
async def root():
    return {"message": "Hello World"}
    # TODO: return model info here


@app.post("/predict")
async def inference_YOLO():
    print("wow")
    logger.info("Received inference request at /predict")

    # hardcoded conversion table
    conv_table = {
        "DotoriMook": "도토리묵",
        "KkakDugi": "깍두기",
        # ...
    }

    # TODO: mount model folder at ../
    # results = model.predict(source='/content/do2.jpeg', save=True)
    ## results format:
    ## image 1/1 /content/do2.jpeg: 640x640 1 DotoriMook, 11.3ms
    # Speed: 5.1ms preprocess, 11.3ms inference, 1.4ms postprocess per image at shape (1, 3, 640, 640)
    # Results saved to runs/detect/predict
    # TODO: get the most of the result
    # results[0].tojson() (json with \n)
    # for result in results:
    #     boxes = result.boxes  # Boxes object for bounding box outputs
    #     masks = result.masks  # Masks object for segmentation masks outputs
    #     keypoints = result.keypoints  # Keypoints object for pose outputs
    #     probs = result.probs  # Probs object for classification outputs
    #     obb = result.obb  # Oriented boxes object for OBB outputs
    #     result.show()  # display to screen
    #     result.save(filename="result.jpg")  # save to disk
    # TODO: 모델 부르면 따로 폴더 만드는데 그거 어뜨케 방지하지??

    return {
        "prediction": "This is a dummy prediction",
        "probability": 0.99,
    }


if __name__ == "__main__":
    uvicorn.run(app, port=8099)
