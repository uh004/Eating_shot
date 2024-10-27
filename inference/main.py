import io

from fastapi import FastAPI, File, UploadFile, Form, Query
from fastapi.responses import UJSONResponse

# TODO: if we were hosting this on a separate server from django...

import csv
import logging
import logstash
import joblib
from sklearn.preprocessing import StandardScaler

import ultralytics
from ultralytics import YOLO
from PIL import ImageDraw, Image, ImageFont

import cv2
import numpy as np
import pandas as pd

ultralytics.checks()

app = FastAPI(default_response_class=UJSONResponse)
host = "logstash"

logger = logging.getLogger("inference")
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler(host, 5000, version=1))

# change the fastapi app port
# uvicorn main:app --port 8000 --reload


## model loading
model = YOLO("models/best.pt")
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

        with open("food_calories.csv", encoding="utf-8") as file:
            csv.reader(file)
            next(file)
            conversion_list = {i: row[0] for i, row in enumerate(file)}

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


def get_food_info(label):
    with open("food_calories.csv", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        # for n, row in enumerate(reader):
        for row in reader:
            if row[0] == label:  # food_name
                return {
                    "food_name": row[0],
                    "energy_kcal": row[1],
                    "weight_g": row[2],
                    "carbohydrates_g": row[3],
                    "protein_g": row[4],
                    "fat_g": row[5],
                    "diabetes_risk_classification": row[6],
                    # "label": row[7],
                    "is_meat": row[8],
                    "is_veg": row[9],
                    "is_seafood": row[10],
                }


def get_closest_food(user_input, n=5):
    scaler = StandardScaler()

    df = pd.read_csv("food_calories.csv", encoding="utf-8").drop(
        columns=["에너지(kcal)"]
    )

    normalized_data = scaler.fit_transform(
        df[
            [
                # "에너지(kcal)", # excluded
                "탄수화물(g)",
                "단백질(g)",
                "지방(g)",
                "고기",
                "채소",
                "해산물",
            ]
        ]
    )

    user_df = pd.DataFrame([user_input])
    normalized_user_input = scaler.transform(user_df)

    distances = np.linalg.norm(normalized_data - normalized_user_input, axis=1)

    # return the top n closest foods (without the new healthy foods from food_calories2)
    return df.iloc[distances.argsort()[:n]].dropna().to_dict("records")


def food_recommendation(user_input):
    df = pd.read_csv("food_calories1-2.csv", encoding="utf-8")

    # based on the manual.txt...
    max_count = max(
        user_input["meat_count"], user_input["veg_count"], user_input["seafood_count"]
    )
    total_count = (
        user_input["meat_count"] + user_input["veg_count"] + user_input["seafood_count"]
    )

    # felt the need to use these as weights (meat, veg, seafood)
    meat_weight = (
        (max_count - user_input["meat_count"]) / total_count if total_count != 0 else 1
    )
    veg_weight = (
        (max_count - user_input["veg_count"]) / total_count if total_count != 0 else 1
    )
    seafood_weight = (
        (max_count - user_input["seafood_count"]) / total_count
        if total_count != 0
        else 1
    )

    def calculate_score(row):
        """
        Calculate a recommendation score for a food item based on its nutritional content and category preferences.

        First, we calculate the nutritional score for calories, carbs, protein, and fat based on the user's remaining intake.

        cal_score = 1 - abs(calories - remaining_calories) / remaining_calories
        carb_score = 1 - abs(carbs - remaining_carbs) / remaining_carbs
        protein_score = 1 - abs(protein - remaining_protein) / remaining_protein
        fat_score = 1 - abs(fat - remaining_fat) / remaining_fat

        Second, we calculate the category preference weight based on the food item's category counts.

        category_weight = (meat_count * meat_weight + veg_count * veg_weight + seafood_count * seafood_weight)

        Finally, we combine the nutritional score and category weight to get the recommendation score.

        score = (preferred portion) * (cal_score + carb_score + protein_score + fat_score) / 4
                +
                (preferred portion) * category_weight
        (you can adjust the weights based on the importance of nutritional fit vs. category preference)

        :param row:
        :return: the recommendation score for the food item
        """
        # Nutritional score
        cal_score = (
            1
            - abs(row["에너지(kcal)"] - user_input["remaining_calories"])
            / user_input["remaining_calories"]
        )
        carb_score = (
            1
            - abs(row["탄수화물(g)"] - user_input["remaining_carbs"])
            / user_input["remaining_carbs"]
        )
        protein_score = (
            1
            - abs(row["단백질(g)"] - user_input["remaining_protein"])
            / user_input["remaining_protein"]
        )
        fat_score = (
            1
            - abs(row["지방(g)"] - user_input["remaining_fat"])
            / user_input["remaining_fat"]
        )

        # Category preference weight
        category_weight = (
            row["고기"] * meat_weight
            + row["채소"] * veg_weight
            + row["해산물"] * seafood_weight
        )

        # add in diabetes friendliness as a factor
        category_weight = category_weight * (row["Diabetes_Friendliness"] + 1) / 3

        # adjust the weights on your preference
        return (
            0.62 * (cal_score + carb_score + protein_score + fat_score) / 4
            + 0.38 * category_weight
        )

    df["Recommendation_Score"] = df.apply(calculate_score, axis=1)

    recommended_foods = df.sort_values(by="Recommendation_Score", ascending=False)

    remaining_calories = user_input["remaining_calories"]
    remaining_carbs = user_input["remaining_carbs"]
    remaining_protein = user_input["remaining_protein"]
    remaining_fat = user_input["remaining_fat"]

    # Sort foods by diabetes-friendliness and calorie efficiency
    sorted_foods = df.sort_values(
        by=["Recommendation_Score", "에너지(kcal)"], ascending=[False, True]
    )

    # Initialize list to store selected foods and track total nutrients
    selected_foods = []
    total_calories, total_carbs, total_protein, total_fat = 0, 0, 0, 0

    # greedy approach: add foods to the list until we reach the nutrient limits
    for _, row in sorted_foods.iterrows():
        food_calories = row["에너지(kcal)"]
        food_carbs = row["탄수화물(g)"]
        food_protein = row["단백질(g)"]
        food_fat = row["지방(g)"]

        # Check if adding this food will exceed remaining allowances
        if (
            total_calories + food_calories <= remaining_calories
            and total_carbs + food_carbs <= remaining_carbs
            and total_protein + food_protein <= remaining_protein
            and total_fat + food_fat <= remaining_fat
        ):
            # Add food to selected list and update totals
            selected_foods.append(row["음식명"])
            total_calories += food_calories
            total_carbs += food_carbs
            total_protein += food_protein
            total_fat += food_fat

    return [selected_foods[0]]  # return the first food item added to the list


@app.get("/")
async def root():
    return {"message": str(model)}


@app.post("/recommendation_score_foods")
def get_recommendation0(user_input: dict):
    """
    # User input for remaining nutritional intake and food category counts
    user_input = {
        "remaining_calories": 520,  # in kcal
        "remaining_carbs": 50,  # in grams
        "remaining_protein": 20,  # in grams
        "remaining_fat": 15,  # in grams
        "고기_count": 2,  # number of meat servings consumed
        "채소_count": 1,  # number of vegetable servings consumed
        "해산물_count": 0,  # number of seafood servings consumed
    }

    :param user_input:
    :return: recommended foods based on the user's remaining nutritional intake and food category counts
    """
    return food_recommendation(user_input)


@app.post("/recommendation_closest_food")
def get_recommendation1(
    user_input: dict,
    n: int = Query(..., description="Number of closest foods to return"),
):
    """
    # find food within this dataset that is closest to a food where it...
    user_input2 = {
        '에너지(kcal)': 1000,  # has 1000 kcal
        '탄수화물(g)': 50,  # has 50g of carbs
        '단백질(g)': 30,  # has 30g of protein
        '지방(g)': 20,  # has 20g of fat
        '고기': 1.0,  # is a meat dish
        '채소': 1.0,  # is a vegetable dish
        '해산물': 0.0  # is not a seafood dish
    }

    :param n:
    :param user_input:
    :return: top 5 closest foods
    """
    return get_closest_food(user_input, n)


@app.post("/recommendation_least_dangerous")
def get_recommendation2(user_input: dict):
    """
    user_input3 = {
        names: ["깍두기", "떡갈비", "도토리묵"],
    }

    index 0: highly dangerous, index 1: moderately dangerous, index 2: friendly

    :param user_input:
    :return:
    """
    # scaler = MinMaxScaler()
    scaler = StandardScaler()
    loaded_model = joblib.load("recommend_food.joblib")
    df = pd.read_csv("food_calories.csv", encoding="utf-8")

    X = df[
        [
            "에너지(kcal)",
            "탄수화물(g)",
            "단백질(g)",
            "지방(g)",
            "고기",
            "채소",
            "해산물",
        ]
    ]  # will adding 고기 채소 해산물 make sense? 머 없는거보다는 낫지 아늘까?
    scaler.fit(X)

    # get the data for the user input(food names)
    input_data = X.iloc[df[df["음식명"].isin(user_input["names"])].index]

    input_data_scaled = scaler.transform(input_data)

    predictions = loaded_model.predict_proba(input_data_scaled)

    friendly_class_index = np.argmax(loaded_model.classes_ == 2)
    least_dangerous_food_index = np.argmax(predictions[:, friendly_class_index])

    # Get the least dangerous food item details
    least_dangerous_food = input_data.iloc[least_dangerous_food_index]

    return {
        "food_name": df.iloc[input_data.iloc[least_dangerous_food_index].name][
            "음식명"
        ],
        "energy_kcal": least_dangerous_food["에너지(kcal)"],
        "carbohydrates_g": least_dangerous_food["탄수화물(g)"],
        "protein_g": least_dangerous_food["단백질(g)"],
        "fat_g": least_dangerous_food["지방(g)"],
    }


@app.get("/nutrition_data")
def get_nutrition_data():
    nutrition_data = []
    with open("food_calories.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            nutrition_data.append(row)
    return nutrition_data


@app.post("/predict")
async def predict(file: UploadFile = File(...), path: str = Form(...)):
    logger.info("Received inference request at /predict")
    filepath = "/".join(path.split("/")[-3:])
    print(filepath)
    # hardcoded conversion table. UNUSED
    # conv_table = {
    #     "DotoriMook": "도토리묵",
    #     "KkakDugi": "깍두기",
    #     "TteokGalbi": "떡갈비",
    #     # ...
    # }

    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    results = model.predict(source=image)
    # [
    # {"name": "\ub5a1\uac08\ube44", "class": 2, "confidence": 0.62822, "box": {"x1": 555.51776, "y1": 53.29996, "x2": 911.6275, "y2": 480.85587}},
    # {"name": "\uae4d\ub450\uae30", "class": 0, "confidence": 0.28041, "box": {"x1": 477.50217, "y1": 469.79544, "x2": 731.09552, "y2": 836.90717}}
    # ]
    logger.info([r.summary() for r in results])
    predictions = [r.summary() for r in results]
    # for pred in predictions[0]:
    #     pred["name"] = conv_table.get(pred["name"], "아무렴뭐어때")
    save_annotated_image(image, results[0], filepath, predictions[0])

    food_info = [get_food_info(pred["name"]) for pred in predictions[0]]
    # [
    # {
    # "food_name": "asdf",
    # "energy_kcal": 100,
    # "weight_g": 100,
    # "carbohydrates_g": 100,
    # "protein_g": 100,
    # "fat_g": 100,
    # "diabetes_risk_classification": 1
    # }
    # ]

    # return predictions[0]  # nested list. escape one level
    return {"predictions": predictions[0], "food_info": food_info}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8099)
