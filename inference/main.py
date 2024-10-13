import io

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import UJSONResponse

# TODO: if we were hosting this on a separate server from django...

import logging
import logstash

import ultralytics
from ultralytics import YOLO
from PIL import ImageDraw, Image, ImageFont

import cv2
import numpy as np

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


def save_annotated_image(image, result, path, pred_result):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    label = result.boxes.cls  # 모델이 예측한 레이블 결과 ex) 30, 11, 2, 15
    fontpath = "models/Pretendard-Bold.ttf"
    font = ImageFont.truetype(fontpath, 25)

    for i in range(len(result.boxes.xyxy)):
        x = int(
            (result.boxes.xyxy[i][0] + result.boxes.xyxy[i][2]) / 2
        )  # 인식한 객체의 바운딩 박스 가로 정가운데
        y = int(
            (result.boxes.xyxy[i][1] + result.boxes.xyxy[i][3]) / 2
        )  # 인식한 객체의 바운딩 박스 세로 정가운데

        conversion_list = {
            0: "도토리묵",
            1: "깍두기",
            2: "떡갈비",
        }
        pred_result = conversion_list[int(label[i])]

        overlay = image.copy()
        left, top, right, bottom = font.getbbox(pred_result)
        width = right - left
        height = bottom - top
        text_size = [width, height]  # 텍스트 가로, 세로 길이

        cv2.rectangle(
            overlay,
            (x - (text_size[0] // 2 + 5), y - (text_size[1] // 2 + 5)),
            (x + (text_size[0] // 2 + 5), y + (text_size[1] // 2 + 10)),
            (0, 0, 0),
            -1,
        )  # 검정색 배경
        alpha = 0.6  # 투명도 설정
        # 텍스트 크기 기반으로 텍스트에 맞춰서 불투명 사각형 생성
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

        img_pil = Image.fromarray(
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        )  # OpenCV 이미지를 PIL 이미지로 변환
        draw = ImageDraw.Draw(img_pil)
        draw.text(
            (x - (text_size[0] // 2), y - (text_size[1] // 2)),
            pred_result,
            font=font,
            fill=(255, 255, 255),
        )  # 한글 텍스트
        # 한글 텍스트 표시

        # PIL 이미지를 다시 OpenCV 이미지로 변환
        image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        cv2.imwrite(f"{path.split('.')[0]}_anno.jpg", image)


@app.get("/")
async def root():
    return {"message": str(model)}


@app.post("/predict")
async def predict(file: UploadFile = File(...), path: str = Form(...)):
    logger.info("Received inference request at /predict")
    filepath = "/".join(path.split("/")[-3:])
    print(filepath)
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
    save_annotated_image(image, results[0], filepath, predictions[0])

    return predictions[0]  # nested list. escape one level


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8099)
