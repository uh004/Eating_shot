from fastapi import FastAPI
import uvicorn

app = FastAPI()


# change the fastapi app port
# uvicorn main:app --port 8000 --reload


@app.get("/")
async def root():
    return {"message": "Hello World"}
    # TODO: return model info here


@app.post("/predict")
async def dummy_inference():
    print("wow")
    return {
        "prediction": "This is a dummy prediction",
        "probability": 0.99,
    }

if __name__ == "__main__":
    uvicorn.run(app, port=8099)
