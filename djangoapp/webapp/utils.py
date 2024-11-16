# utils.py (엉망진창..)
import random
from datetime import datetime, timedelta

import httpx
import numpy as np
import pandas as pd
from core.settings import INFERENCE_SERVER_URL
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from events.models import HospitalAlarm, PillAlarm
from users.models import (
    BloodPressure,
    BloodSugar,
    CustomUser,
    Diet,
    Exercise,
    ExerciseType,
    HbA1c,
)

timeout = httpx.Timeout(connect=30.0, read=30.0, write=30.0, pool=30.0)


def handle_form(
    request, form_class, template_name, redirect_url, instance=None, extra_context=None
):
    if request.method == "POST":
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = form_class(instance=instance)

    context = {"form": form}
    if extra_context:
        context.update(extra_context)

    return render(request, template_name, context)


def calculate_totals(meals):
    total_calories = 0
    total_carbohydrates = 0
    total_protein = 0
    total_fat = 0
    meal_calories = {}

    for meal in meals:
        food_info = meal.result.result_data["food_info"]
        meal_total_calories = sum(int(food["energy_kcal"]) for food in food_info)
        meal_calories[meal.id] = meal_total_calories
        total_calories += meal_total_calories
        total_carbohydrates += sum(int(food["carbohydrates_g"]) for food in food_info)
        total_protein += sum(int(food["protein_g"]) for food in food_info)
        total_fat += sum(int(food["fat_g"]) for food in food_info)

    print(total_calories, total_carbohydrates, total_protein, total_fat, meal_calories)

    return total_calories, total_carbohydrates, total_protein, total_fat, meal_calories


def calculate_weekly_totals(meals_last_week):
    total_calories_week = 0
    total_carbohydrates_week = 0
    total_protein_week = 0
    total_fat_week = 0

    for meal in meals_last_week:
        food_info = meal.result.result_data["food_info"]
        total_calories_week += sum(int(food["energy_kcal"]) for food in food_info)
        total_carbohydrates_week += sum(
            int(food["carbohydrates_g"]) for food in food_info
        )
        total_protein_week += sum(int(food["protein_g"]) for food in food_info)
        total_fat_week += sum(int(food["fat_g"]) for food in food_info)

    return (
        total_calories_week,
        total_carbohydrates_week,
        total_protein_week,
        total_fat_week,
    )


def count_food_types(meals):
    meat_count = 0
    veg_count = 0
    seafood_count = 0

    for meal in meals:
        food_info = meal.result.result_data["food_info"]
        for food in food_info:
            if food["is_meat"] == 1.0:
                meat_count += 1
            if food["is_veg"] == 1.0:
                veg_count += 1
            if food["is_seafood"] == 1.0:
                seafood_count += 1

    return meat_count, veg_count, seafood_count


def prepare_meal_context(request):
    context = {}
    meals = Diet.objects.filter(user=request.user).prefetch_related("result")
    if meals.exists():
        context["meals"] = meals

        max_calories = CustomUser.objects.get(id=request.user.id).weight * 35
        max_carbohydrates = (
            max_calories // 8
        )  # fixed value -> /= 8 of today's eaten calories
        max_protein = int(CustomUser.objects.get(id=request.user.id).weight * 0.8)
        max_fat = 50

        context["max_calories"] = max_calories
        context["max_carbohydrates"] = max_carbohydrates
        context["max_protein"] = max_protein
        context["max_fat"] = max_fat

        # {
        # "predictions": [
        # {"name": "\uc54c\ubc25", "class": 0, "confidence": 0.79386, "box": {"x1": 0.0, "y1": 15.278, "x2": 1435.80652, "y2": 1041.46191}},
        # {"name": "\uc794\uce58\uad6d\uc218", "class": 20, "confidence": 0.6759, "box": {"x1": 0.0, "y1": 15.12831, "x2": 1406.91821, "y2": 1046.10669}}
        # ],
        # "food_info": [
        # {"food_name": "\uc54c\ubc25", "energy_kcal": "607", "weight_g": "400", "carbohydrates_g": "92", "protein_g": "15", "fat_g": "3", "diabetes_risk_classification": "0"},
        # {"food_name": "\uc794\uce58\uad6d\uc218", "energy_kcal": "484", "weight_g": "600", "carbohydrates_g": "90", "protein_g": "17", "fat_g": "5", "diabetes_risk_classification": "0"}
        # ]
        # }

        total_calories, total_carbohydrates, total_protein, total_fat, meal_calories = (
            calculate_totals(meals)
        )

        context["total_calories"] = total_calories
        context["total_carbohydrates"] = total_carbohydrates
        context["total_protein"] = total_protein
        context["total_fat"] = total_fat
        context["meal_calories"] = meal_calories

        # {
        #     "remaining_calories": 520,
        #     "remaining_carbs": 50,
        #     "remaining_protein": 20,
        #     "remaining_fat": 15,
        #     "고기_count": 2,
        #     "채소_count": 1,
        #     "해산물_count": 0
        # }
        remaining_calories = max_calories - total_calories
        remaining_carbs = max_carbohydrates - total_carbohydrates
        remaining_protein = max_protein - total_protein
        remaining_fat = max_fat - total_fat

        if remaining_calories <= 0:
            remaining_calories = 1
        if remaining_carbs <= 0:
            remaining_carbs = 1
        if remaining_protein <= 0:
            remaining_protein = 1
        if remaining_fat <= 0:
            remaining_fat = 1

        meat_count, veg_count, seafood_count = count_food_types(meals)

        data = {
            "remaining_calories": remaining_calories,
            "remaining_carbs": remaining_carbs,
            "remaining_protein": remaining_protein,
            "remaining_fat": remaining_fat,
            "meat_count": meat_count,
            "veg_count": veg_count,
            "seafood_count": seafood_count,
        }
        print(data)
        with httpx.Client() as client:
            response = client.post(
                f"{INFERENCE_SERVER_URL}/recommendation_score_foods",
                json=data,
                timeout=timeout,
            )
        context["recommendation_foods"] = response.json()  # python list of foods
        # context["recommendation_foods"] = ["ㅁㅁㄴㅇㄹ"]

    return context


def prepare_exercise_context(request):
    predifined_indoor_exercises = [
        "체조",
        "에어로빅",
        "수영",
        "스케이팅",
        "볼링",
        "탁구",
        "계단오르내리기",
        "배드민턴",
        "배구",
        "웨이트 트레이닝",
        "스쿼트",
        "윗몸 일으키기",
        "팔굽혀펴기",
    ]  # hardcoded values of indoor exercises
    # what would be better? make a django custom command for importing these values to the database?
    current_all_exercise_types = ExerciseType.objects.values_list(
        "name", "exercise_category"
    )
    df = pd.DataFrame(
        list(current_all_exercise_types), columns=["운동 종류", "운동 분류"]
    )

    df["location"] = np.where(df["운동 종류"].isin(predifined_indoor_exercises), 1, 0)
    df["type"] = np.where(df["운동 분류"] == "유산소", 1, 0)

    # currently just randomly selecting an exercise
    def exercise_recommend(user_input):
        more_ex = (
            user_input[2:].index(min(user_input[2:]))
            if abs(user_input[2] - user_input[3]) >= 1
            else 0
        )

        if user_input[1] >= 18 or user_input[1] <= 5:
            recommend_list = df[
                df["운동 종류"].isin(df[df["location"] == 1]["운동 종류"])
            ]
        else:
            recommend_list = df[df["type"] == abs(1 - more_ex)]

        # similarity_scores = cosine_similarity(
        # recommend_list[recommend_list.columns[1:3]], [user_input[1:3]]
        # )
        # defined but not actually used in the function
        # commented out because of missing import

        return recommend_list["운동 종류"][:5].iloc[random.randint(0, 4)]

    max_calories = 1000
    remaining_calories = max_calories - sum(
        exercise.exercise_calories
        for exercise in Exercise.objects.filter(user=request.user)
    )  # defined but not actually used in the function

    count_exercise_cardio = sum(
        item["count"]
        for item in Exercise.objects.values("exercise_type__exercise_category")
        .annotate(count=Count("id"))
        .filter(Q(exercise_type__exercise_category="유산소"))
    )
    count_exercise_weights = sum(
        item["count"]
        for item in Exercise.objects.values("exercise_type__exercise_category")
        .annotate(count=Count("id"))
        .filter(Q(exercise_type__exercise_category="무산소"))
    )

    context = {
        "exercise_recommendation": exercise_recommend(
            [
                remaining_calories,
                datetime.now().hour,
                count_exercise_cardio,
                count_exercise_weights,
            ]
        ),
        "exercises": Exercise.objects.filter(user=request.user),
        "total_calories": sum(
            [
                exercise.exercise_calories
                for exercise in Exercise.objects.filter(user=request.user)
            ]
        ),
    }

    return context


def prepare_blood_context(request):
    context = {}
    # get all blood related data(blood sugar, blood pressure, hba1c) and align all in one list

    blood_sugar = BloodSugar.objects.filter(user=request.user)
    blood_pressure = BloodPressure.objects.filter(user=request.user)
    hba1c = HbA1c.objects.filter(user=request.user)

    context["blood1_data"] = blood_sugar
    context["blood2_data"] = blood_pressure
    context["blood3_data"] = hba1c

    return context


def prepare_mypage_context(request):
    context = {}
    user_info = request.user
    context["user_info"] = user_info
    conversion_table = {
        "type1": "1형 당뇨",
        "type2": "2형 당뇨",
        "gestational": "임신성 당뇨",
        "prediabetes": "내당증",
        "high": "고혈압",
        "low": "저혈압",
        "hyperlipidemia": "고지혈증",
        "obesity": "비만",
    }
    health_conditions = user_info.health_conditions.split(",")
    context["health_conditions"] = [
        conversion_table[condition] for condition in health_conditions
    ]
    weekday_conversion_table = {
        "mon": "월",
        "tue": "화",
        "wed": "수",
        "thu": "목",
        "fri": "금",
        "sat": "토",
        "sun": "일",
    }
    alarm_object = PillAlarm.objects.filter(user=request.user)
    for alarm in alarm_object:
        alarm.weekday = [
            weekday_conversion_table[day] for day in alarm.weekday.split(",")
        ]
    context["pill_alarm"] = alarm_object
    context["hospital_alarm"] = HospitalAlarm.objects.filter(user=request.user)
    context["weekdays"] = ["월", "화", "수", "목", "금", "토", "일"]

    return context


# for report
def prepare_meal_data(request):
    context = {}
    meals = Diet.objects.filter(user=request.user).prefetch_related("result")

    context["meals"] = meals
    context["total_calories"] = 0
    context["total_carbohydrates"] = 0
    context["total_protein"] = 0
    context["total_fat"] = 0
    context["meal_calories"] = {}
    context["total_calories_week"] = 0
    context["total_carbohydrates_week"] = 0
    context["total_protein_week"] = 0
    context["total_fat_week"] = 0
    context["meat_count"] = 0
    context["veg_count"] = 0
    context["seafood_count"] = 0
    context["meat_count_week"] = 0
    context["veg_count_week"] = 0
    context["seafood_count_week"] = 0
    context["max_calories"] = 0
    context["max_carbohydrates"] = 0
    context["max_protein"] = 0
    context["max_fat"] = 0

    if meals.exists():
        max_calories = CustomUser.objects.get(id=request.user.id).weight * 35
        context["max_calories"] = max_calories
        context["max_carbohydrates"] = max_calories // 8
        context["max_protein"] = int(
            CustomUser.objects.get(id=request.user.id).weight * 0.8
        )
        context["max_fat"] = 50

        total_calories, total_carbohydrates, total_protein, total_fat, meal_calories = (
            calculate_totals(meals)
        )
        context["total_calories"] = total_calories
        context["total_carbohydrates"] = total_carbohydrates
        context["total_protein"] = total_protein
        context["total_fat"] = total_fat
        context["meal_calories"] = meal_calories

        meals_last_week = Diet.objects.filter(
            user=request.user, date__gte=datetime.now() - timedelta(days=7)
        ).prefetch_related("result")
        (
            total_calories_week,
            total_carbohydrates_week,
            total_protein_week,
            total_fat_week,
        ) = calculate_weekly_totals(meals_last_week)
        context["total_calories_week"] = total_calories_week
        context["total_carbohydrates_week"] = total_carbohydrates_week
        context["total_protein_week"] = total_protein_week
        context["total_fat_week"] = total_fat_week

        meat_count, veg_count, seafood_count = count_food_types(meals)
        context["meat_count"] = meat_count
        context["veg_count"] = veg_count
        context["seafood_count"] = seafood_count

        meat_count_week, veg_count_week, seafood_count_week = count_food_types(
            meals_last_week
        )
        context["meat_count_week"] = meat_count_week
        context["veg_count_week"] = veg_count_week
        context["seafood_count_week"] = seafood_count_week

    return context


def prepare_exercise_data(request):
    context = {}

    exercises = Exercise.objects.filter(user=request.user)
    if exercises:
        context["total_exercise_calories"] = sum(
            exercise.exercise_calories for exercise in exercises
        )
        context["total_exercise_time"] = sum(
            exercise.exercise_time for exercise in exercises
        )

        # Weekly exercise data
        exercises_last_week = Exercise.objects.filter(
            user=request.user, date__gte=datetime.now() - timedelta(days=7)
        )
        context["total_exercise_calories_week"] = sum(
            exercise.exercise_calories for exercise in exercises_last_week
        )
        context["total_exercise_time_week"] = sum(
            exercise.exercise_time for exercise in exercises_last_week
        )

        context["count_exercise_cardio"] = sum(
            item["count"]
            for item in Exercise.objects.filter(user=request.user)
            .values("exercise_type__exercise_category")
            .annotate(count=Count("id"))
            .filter(Q(exercise_type__exercise_category="유산소"))
        )
        context["count_exercise_weights"] = sum(
            item["count"]
            for item in Exercise.objects.filter(user=request.user)
            .values("exercise_type__exercise_category")
            .annotate(count=Count("id"))
            .filter(Q(exercise_type__exercise_category="무산소"))
        )

        context["count_exercise_cardio_week"] = sum(
            item["count"]
            for item in Exercise.objects.filter(
                date__gte=datetime.now() - timedelta(days=7)
            )
            .values("exercise_type__exercise_category")
            .annotate(count=Count("id"))
            .filter(Q(exercise_type__exercise_category="유산소"))
        )
        context["count_exercise_weights_week"] = sum(
            item["count"]
            for item in Exercise.objects.filter(
                date__gte=datetime.now() - timedelta(days=7)
            )
            .values("exercise_type__exercise_category")
            .annotate(count=Count("id"))
            .filter(Q(exercise_type__exercise_category="무산소"))
        )

    return context


def prepare_blood_data(request):
    context = {}
    blood_sugar = BloodSugar.objects.filter(user=request.user)
    blood_pressure = BloodPressure.objects.filter(user=request.user)
    hba1c = HbA1c.objects.filter(user=request.user)

    last_day_blood_sugar = BloodSugar.objects.filter(
        user=request.user, date__gte=datetime.now() - timedelta(days=1)
    )
    last_day_blood_pressure = BloodPressure.objects.filter(
        user=request.user, date__gte=datetime.now() - timedelta(days=1)
    )
    last_day_hba1c = HbA1c.objects.filter(
        user=request.user, date__gte=datetime.now() - timedelta(days=1)
    )

    if last_day_blood_sugar:
        mean_blood_sugar = sum(data.blood_sugar for data in blood_sugar) / len(
            blood_sugar
        )
        context["mean_blood_sugar"] = int(mean_blood_sugar)
        context["max_blood_sugar"] = max(data.blood_sugar for data in blood_sugar)
        context["min_blood_sugar"] = min(data.blood_sugar for data in blood_sugar)

    if last_day_blood_pressure:
        mean_blood_pressure_systolic = sum(
            data.systolic for data in blood_pressure
        ) / len(blood_pressure)
        mean_blood_pressure_diastolic = sum(
            data.diastolic for data in blood_pressure
        ) / len(blood_pressure)
        context["mean_blood_pressure_systolic"] = int(mean_blood_pressure_systolic)
        context["mean_blood_pressure_diastolic"] = int(mean_blood_pressure_diastolic)
        context["max_blood_pressure_systolic"] = max(
            data.systolic for data in blood_pressure
        )
        context["max_blood_pressure_diastolic"] = max(
            data.diastolic for data in blood_pressure
        )
        context["min_blood_pressure_systolic"] = min(
            data.systolic for data in blood_pressure
        )
        context["min_blood_pressure_diastolic"] = min(
            data.diastolic for data in blood_pressure
        )

    if last_day_hba1c:
        context["hb1ac"] = hba1c[0].hba1c  # only one data per day

    return context
