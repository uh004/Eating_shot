from fastapi import FastAPI
import uvicorn
import logging
import logstash

app = FastAPI()
host = "logstash"

logger = logging.getLogger("inference")
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler(host, 5000, version=1))


# change the fastapi app port
# uvicorn main:app --port 8000 --reload


@app.get("/")
async def root():
    return {"message": "Hello World"}
    # TODO: return model info here


@app.post("/predict")
async def dummy_inference():
    print("wow")
    logger.info("Received inference request at /predict")
    return {
        "prediction": "This is a dummy prediction",
        "probability": 0.99,
    }


if __name__ == "__main__":
    uvicorn.run(app, port=8099)
