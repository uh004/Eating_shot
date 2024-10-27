import json

import httpx
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.http import JsonResponse

from .utils import (
    handle_form,
    prepare_meal_context,
    prepare_exercise_context,
    prepare_blood_context,
    prepare_mypage_context,
    prepare_meal_data,
    prepare_exercise_data,
    prepare_blood_data,
)


# from ai_workload.kafka.producer import send_inference_task
from ai_workload.tasks import process_inference_task
from ai_workload.models import InferenceTask, InferenceResult
from users.models import (
    Exercise,
    Diet,
    ExerciseType,
    BloodSugar,
    BloodPressure,
    HbA1c,
    CustomUser,
    FoodCalories,
)
from events.models import PillAlarm, HospitalAlarm
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    HealthInfoForm,
    BloodSugarForm,
    BloodPressureForm,
    HbA1cForm,
    ExerciseForm,
    DietForm,
    MyPageReviseForm,
    PillAlarmForm,
    HospitalAlarmForm,
)
from datetime import datetime

timeout = httpx.Timeout(connect=30.0, read=30.0, write=30.0, pool=30.0)


@login_required
def index(request):
    if request.user.height is None:
        return redirect("info")
    return render(request, "users/home.html")


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
        else:
            error_messages = "아이디 또는 비밀번호가 올바르지 않습니다."
    else:
        form = CustomAuthenticationForm()
        error_messages = None
    return render(
        request, "users/login.html", {"form": form, "error_messages": error_messages}
    )


@login_required
def info_view(request):
    if request.method == "POST":
        form = HealthInfoForm(request.POST)
        if form.is_valid():
            user = request.user
            user.height = form.cleaned_data["height"]
            user.weight = form.cleaned_data["weight"]
            # user.age = form.cleaned_data["age"]
            user.birthdate = form.cleaned_data["birthdate"]
            user.gender = form.cleaned_data["gender"]
            user.goal = form.cleaned_data["goal"]
            user.health_conditions = ",".join(form.cleaned_data["health_conditions"])
            user.save()
            return redirect("index")
    else:
        form = HealthInfoForm()
    return render(request, "users/info.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


# TODO: change password
def change_password(request):
    user = request.user
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, "users/change_password.html", {"form": form})


#
def load_content(request, menu):
    pages = ["diet", "exercise", "blood", "report", "mypage"]
    template_name = f"users/{menu}.html"

    context = {}

    match menu:
        case "report":
            context.update(prepare_meal_data(request))
            context.update(prepare_exercise_data(request))
            context.update(prepare_blood_data(request))

        case "diet":
            context.update(prepare_meal_context(request))
        case "exercise":
            context.update(prepare_exercise_context(request))
        case "blood":
            context.update(prepare_blood_context(request))
        case "mypage":
            context.update(prepare_mypage_context(request))
        case _:
            pass

    return render(request, template_name, context)


@login_required
def exercise_list(request):
    exercises_by_type = ExerciseType.objects.annotate(exercise_count=Count("exercise"))

    return render(
        request,
        "users/exercise_list.html",
        {"exercises_by_type": exercises_by_type},
    )


@login_required
def diet_form(request, id=None):
    if id:
        diet = Diet.objects.get(id=id, user=request.user)
    else:
        diet = Diet(user=request.user)

    if request.method == "POST":
        form = DietForm(request.POST, request.FILES, instance=diet)
        if form.is_valid():
            diet = form.save(commit=False)
            diet.user = request.user
            diet.save()

            # Create an InferenceTask instance
            inference_task = InferenceTask.objects.create(
                user=request.user, photo=diet.image, status="PENDING"
            )

            # Queue the inference task
            # send_inference_task(inference_task.id) # Kafka
            process_inference_task.delay(inference_task.id)  # Celery

            # Wait for the inference result to be ready
            inference_task.refresh_from_db()
            while inference_task.status != "COMPLETED":
                inference_task.refresh_from_db()
                if inference_task.status == "FAILED":
                    return JsonResponse({"error": "Inference task failed"}, status=500)
                else:
                    pass

            return redirect("index")
    else:
        form = DietForm(instance=diet)
    return render(request, "users/diet_form.html", {"form": form})


def get_nutrition_data(food_name):
    food_data = {
        "food_name": "",
        "energy_kcal": 0,
        "weight_g": 0,
        "carbohydrates_g": 0,
        "protein_g": 0,
        "fat_g": 0,
    }
    try:
        nutrition = FoodCalories.objects.get(food_name=food_name)
        food_data["food_name"] = food_name
        food_data["energy_kcal"] = nutrition.energy_kcal
        food_data["weight_g"] = nutrition.weight_g
        food_data["carbohydrates_g"] = nutrition.carbohydrates_g
        food_data["protein_g"] = nutrition.protein_g
        food_data["fat_g"] = nutrition.fat_g
    except FoodCalories.DoesNotExist:
        return False

    return food_data


@login_required
def update_meal(request, meal_id, existing_food_name):
    """

    :param request:
    :param meal_id: target meal id
    :param existing_food_name: target nutrient name
    :return:
    """
    try:
        target_big = InferenceResult.objects.get(
            id=Diet.objects.get(id=meal_id).result_id
        )
        changeable_food_info_names = [
            x["food_name"]
            for x in target_big.result_changeable_food_info
            if x["food_name"] != "TOTAL"
        ]

        if request.method == "PUT":
            # when editing food name
            data = json.loads(request.body)
            name = data.get("name")

            to_food_info = get_nutrition_data(name)
            if to_food_info:
                if existing_food_name in changeable_food_info_names:
                    target_big.result_changeable_food_info = [
                        item
                        for item in target_big.result_changeable_food_info
                        if item.get("food_name") != existing_food_name
                    ]
                    target_big.result_changeable_food_info.append(to_food_info)
                else:
                    return JsonResponse(
                        {"success": False, "message": "Already exists"}, status=304
                    )
            else:
                return JsonResponse(
                    {"success": False, "message": "No Such Food Exist"}, status=404
                )
            target_big.save()
            return JsonResponse({"success": True}, status=200)

        elif request.method == "DELETE":
            # when deleting food names
            if len(changeable_food_info_names) == 1:
                return JsonResponse(
                    {"success": False, "message": "마지막 음식은 삭제할 수 없습니다."},
                    status=400,
                )
            if existing_food_name in changeable_food_info_names:
                target_big.result_changeable_food_info = [
                    item
                    for item in target_big.result_changeable_food_info
                    if item.get("food_name") != existing_food_name
                ]
            else:
                return JsonResponse(
                    {"success": False, "message": "Not found"}, status=404
                )
            target_big.save()
            return JsonResponse({"success": True}, status=200)

        elif request.method == "POST":
            # when adding food names
            data = json.loads(request.body)
            name = data.get("name")

            to_food_info = get_nutrition_data(name)
            if to_food_info:
                target_big.result_changeable_food_info.append(to_food_info)
            else:
                return JsonResponse(
                    {"success": False, "message": "No Such Food Exist"}, status=404
                )
            target_big.save()
            return JsonResponse({"success": True}, status=200)
    except Diet.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "something went wrong. no meal record found"},
            status=404,
        )

    return JsonResponse(
        {"success": False, "message": "Invalid request method"}, status=400
    )


@login_required
def blood_data_view(request, data_type, id=None):
    model_map = {
        "blood_sugar": BloodSugar,
        "blood_pressure": BloodPressure,
        "hba1c": HbA1c,
    }
    form_map = {
        "blood_sugar": BloodSugarForm,
        "blood_pressure": BloodPressureForm,
        "hba1c": HbA1cForm,
    }
    template_map = {
        "blood_sugar": "users/blood_form1.html",
        "blood_pressure": "users/blood_form2.html",
        "hba1c": "users/blood_form3.html",
    }

    model = model_map.get(data_type)
    form_class = form_map.get(data_type)
    template_name = template_map.get(data_type)

    if not model or not form_class or not template_name:
        return redirect("index")

    instance = (
        model.objects.get(id=id, user=request.user) if id else model(user=request.user)
    )
    return handle_form(request, form_class, template_name, "index", instance=instance)


@login_required
def exercise_form(request, exercise_type_id, exercise_id=None):
    if exercise_id is None:
        exercise = Exercise(user=request.user, exercise_type_id=exercise_type_id)
    else:
        try:
            exercise = Exercise.objects.get(
                id=exercise_id, user=request.user, exercise_type_id=exercise_type_id
            )
        except Exercise.DoesNotExist:
            return redirect("exercise_list")

    if request.method == "POST":
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            # exercise = form.save(commit=False)
            # exercise.user = request.user
            # exercise.exercise_type = ExerciseType.objects.get(id=exercise_id)
            # exercise.save()
            form.save()
            return redirect("index")
    else:
        form = ExerciseForm(instance=exercise)
    return render(
        request,
        "users/exercise_form.html",
        # {
        #     "form": form,
        #     "exercise_name": ExerciseType.objects.get(id=exercise_id).name,
        #     "calories_per_hour": ExerciseType.objects.get(
        #         id=exercise_id
        #     ).calories_per_hour,
        # },
        {
            "form": form,
            "exercise_name": exercise.exercise_type.name,
            "calories_per_hour": exercise.exercise_type.calories_per_hour,
        },
    )


@login_required
def mypage_revise_form(request):
    user = get_object_or_404(CustomUser, pk=request.user.pk)

    if request.method == "POST":
        form = MyPageReviseForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        initial_data = {
            "email": user.email,
            "height": user.height,
            "weight": user.weight,
            "health_conditions": user.health_conditions.split(","),
        }
        form = MyPageReviseForm(instance=user, initial=initial_data)

    return render(request, "users/mypage_revise_form.html", {"form": form})


@login_required
def get_chart_data(request, chart_type, detail_type):
    # if request.method != "GET":
    #     return JsonResponse({"error": "GET method required."}, status=400)
    """
    <h3>일주일 당뇨 지표</h3>
    <select id="options" onchange="showButton()">
        <option name="options" value="option1">혈당</option>
        <option name="options" value="option2">혈압</option>
        <option name="options" value="option3">당화혈색소</option>
    </select>

    <select class="blood_detail" id="blood1_check" onchange="showButton()">
        <option>아침 식전</option>
        <option>점심 식전</option>
        <option>저녁 식전</option>
        <option>아침 식후</option>
        <option>점심 식후</option>
        <option>저녁 식후</option>
        <option>공복</option>
    </select>

    <select class="blood_detail" id="blood2_check" onchange="showButton()">
        <option>수축기</option>
        <option>이완기</option>
    </select>

    <div style="width: 400px; height: 330px; background-color: white; border-radius: 20px;">
        <canvas id="canvas" width="400px" height="30px"></canvas>
    </div>
    """
    converison_table = {
        # "option1": "혈당",
        # "option2": "혈압",
        # "option3": "당화혈색소",
        "morning_before": "아침 식전",
        "lunch_before": "점심 식전",
        "dinner_before": "저녁 식전",
        "morning_after": "아침 식후",
        "lunch_after": "점심 식후",
        "dinner_after": "저녁 식후",
        "vacant": "공복",
        # separate
        "systolic": "systolic",
        "diastolic": "diastolic",
        "default": "default",
    }
    detail_type = converison_table.get(detail_type, -1)
    if detail_type == -1:
        return JsonResponse({"error": "Invalid detail type."}, status=400)

    match (chart_type, detail_type):
        case "option1", detail_type:
            blood_sugar = BloodSugar.objects.filter(user=request.user, time=detail_type)
            labels = [datetime.strftime(data.date, "%Y%m%d") for data in blood_sugar]
            data = [data.blood_sugar for data in blood_sugar]
        case "option2", detail_type:
            blood_pressure = BloodPressure.objects.filter(user=request.user)
            labels = [datetime.strftime(data.date, "%Y%m%d") for data in blood_pressure]
            if detail_type == "systolic":
                data = [data.systolic for data in blood_pressure]
            elif detail_type == "diastolic":
                data = [data.diastolic for data in blood_pressure]
            else:
                return JsonResponse({"error": "Invalid detail type."}, status=400)
        case "option3", detail_type:
            hba1c = HbA1c.objects.filter(user=request.user)
            labels = [datetime.strftime(data.date, "%Y%m%d") for data in hba1c]
            data = [data.hba1c for data in hba1c]
        case _:
            return JsonResponse({"error": "Invalid chart type."}, status=400)

    fdata = {
        "labels": labels,
        "datasets": [
            {
                "data": data,
                "backgroundColor": "rgba(255, 99, 132, 0.2)",
                "borderColor": "rgba(255, 99, 132, 1)",
                "borderWidth": 1,
            }
        ],
    }
    return JsonResponse(fdata)


@login_required
def food_detail(request, id):
    meal = get_object_or_404(Diet, pk=id)
    meal.image.name = meal.image.name.split(".")[0] + "_anno.jpg"
    meal.result_names_list = meal.result.result_names_comma_separated.split(",")
    a = [
        {
            "food_name": "\uc54c\ubc25",
            "energy_kcal": "607",
            "weight_g": "400",
            "carbohydrates_g": "92",
            "protein_g": "15",
            "fat_g": "3",
            "diabetes_risk_classification": "0",
        },
        {
            "food_name": "\uc794\uce58\uad6d\uc218",
            "energy_kcal": "484",
            "weight_g": "600",
            "carbohydrates_g": "90",
            "protein_g": "17",
            "fat_g": "5",
            "diabetes_risk_classification": "0",
        },
        {
            "food_name": "TOTAL",
            "energy_kcal": "1091",
            "weight_g": "1000",
            "carbohydrates_g": "182",
            "protein_g": "32",
            "fat_g": "8",
        },
    ]
    food_info = meal.result.result_changeable_food_info[-1]
    meal.total_carbohydrates = int(food_info["carbohydrates_g"])
    meal.total_protein = int(food_info["protein_g"])
    # meal.total_fat = sum(int(food["fat_g"]) for food in food_info)
    meal.total_fat = int(food_info["fat_g"])
    return render(request, "users/food_detail.html", {"meal": meal})


@login_required
def pill_alarm(request, id=None):
    if id:
        alarm = get_object_or_404(PillAlarm, pk=id)
    else:
        alarm = PillAlarm(user=request.user)

    if request.method == "POST":
        form = PillAlarmForm(request.POST, instance=alarm)
        if form.is_valid():
            alarm = form.save(commit=False)
            alarm.user = request.user
            alarm.save()
            return redirect("index")
    else:
        form = PillAlarmForm(instance=alarm)

    return render(request, "users/pill_alarm.html", {"form": form})


@login_required
def hospital_alarm(request, id=None):
    if id:
        alarm = get_object_or_404(HospitalAlarm, pk=id)
    else:
        alarm = HospitalAlarm(user=request.user)

    if request.method == "POST":
        form = HospitalAlarmForm(request.POST, instance=alarm)
        if form.is_valid():
            alarm = form.save(commit=False)
            alarm.user = request.user
            alarm.save()
            return redirect("index")
    else:
        form = HospitalAlarmForm(instance=alarm)

    return render(request, "users/hospital_alarm.html", {"form": form})


@login_required
def delete_request(request, menu, id):
    if request.method == "DELETE":
        match menu:
            case "meal":
                Diet.objects.filter(id=id).delete()
            case "exercise":
                Exercise.objects.filter(id=id).delete()
            case "blood1":
                BloodSugar.objects.filter(id=id).delete()
            case "blood2":
                BloodPressure.objects.filter(id=id).delete()
            case "blood3":
                HbA1c.objects.filter(id=id).delete()
            case "pill_alarm":
                PillAlarm.objects.filter(id=id).delete()
            case "hospital_alarm":
                HospitalAlarm.objects.filter(id=id).delete()
            case _:
                pass
        return JsonResponse({"message": "Deleted successfully."}, status=200)
    return JsonResponse({"error": "Invalid method."}, status=400)
