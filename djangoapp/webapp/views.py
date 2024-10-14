import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.http import JsonResponse

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
from datetime import datetime, timedelta


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

    # TODO: reducing duplicate code
    match menu:
        case "report":
            meals = Diet.objects.filter(user=request.user).prefetch_related("result")
            exercises = Exercise.objects.filter(user=request.user)
            blood_sugar = BloodSugar.objects.filter(user=request.user)
            blood_pressure = BloodPressure.objects.filter(user=request.user)
            hba1c = HbA1c.objects.filter(user=request.user)

            if len(meals) > 0:
                # meal data
                context["meals"] = meals

                max_calories = CustomUser.objects.get(id=request.user.id).weight * 35
                context["max_calories"] = max_calories
                context["max_carbohydrates"] = 100  # fixed value
                context["max_protein"] = int(
                    CustomUser.objects.get(id=request.user.id).weight
                    * 0.8  # for proteins, 0.8g per kg
                )
                context["max_fat"] = 50  # fixed value

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

                total_calories = 0
                total_carbohydrates = 0
                total_protein = 0
                total_fat = 0

                meal_calories = {}

                for meal in meals:
                    food_info = meal.result.result_data["food_info"]
                    meal_total_calories = sum(
                        int(food["energy_kcal"]) for food in food_info
                    )
                    meal_calories[meal.id] = meal_total_calories
                    total_calories += sum(
                        int(food["energy_kcal"]) for food in food_info
                    )
                    total_carbohydrates += sum(
                        int(food["carbohydrates_g"]) for food in food_info
                    )
                    total_protein += sum(int(food["protein_g"]) for food in food_info)
                    total_fat += sum(int(food["fat_g"]) for food in food_info)

                context["total_calories"] = total_calories
                context["total_carbohydrates"] = total_carbohydrates
                context["total_protein"] = total_protein
                context["total_fat"] = total_fat
                context["meal_calories"] = meal_calories

                # weekly data
                total_calories_week = 0
                total_carbohydrates_week = 0
                total_protein_week = 0
                total_fat_week = 0

                meals_last_week = Diet.objects.filter(
                    user=request.user, date__gte=datetime.now() - timedelta(days=7)
                ).prefetch_related("result")

                for meal in meals_last_week:
                    food_info = meal.result.result_data["food_info"]
                    total_calories_week += sum(
                        int(food["energy_kcal"]) for food in food_info
                    )
                    total_carbohydrates_week += sum(
                        int(food["carbohydrates_g"]) for food in food_info
                    )
                    total_protein_week += sum(
                        int(food["protein_g"]) for food in food_info
                    )
                    total_fat_week += sum(int(food["fat_g"]) for food in food_info)

                context["total_calories_week"] = total_calories_week
                context["total_carbohydrates_week"] = total_carbohydrates_week
                context["total_protein_week"] = total_protein_week
                context["total_fat_week"] = total_fat_week

            if len(exercises) > 0:
                # exercise data
                context["total_exercise_calories"] = sum(
                    [
                        exercise.exercise_calories
                        for exercise in Exercise.objects.filter(user=request.user)
                    ]
                )
                context["total_exercise_time"] = sum(
                    [
                        exercise.exercise_time
                        for exercise in Exercise.objects.filter(user=request.user)
                    ]
                )

                # weekly exercise data
                context["total_exercise_calories_week"] = sum(
                    [
                        exercise.exercise_calories
                        for exercise in Exercise.objects.filter(
                            user=request.user,
                            date__gte=datetime.now() - timedelta(days=7),
                        )
                    ]
                )
                context["total_exercise_time_week"] = sum(
                    [
                        exercise.exercise_time
                        for exercise in Exercise.objects.filter(
                            user=request.user,
                            date__gte=datetime.now() - timedelta(days=7),
                        )
                    ]
                )

            if len(blood_sugar) > 0:
                # blood data for today(under 24 hours)
                blood_sugar = BloodSugar.objects.filter(
                    user=request.user, date__gte=datetime.now() - timedelta(days=1)
                )
                blood_pressure = BloodPressure.objects.filter(
                    user=request.user, date__gte=datetime.now() - timedelta(days=1)
                )
                hba1c = HbA1c.objects.filter(
                    user=request.user, date__gte=datetime.now() - timedelta(days=1)
                )

                mean_blood_sugar = sum(
                    [data.blood_sugar for data in blood_sugar]
                ) / len(blood_sugar)
                max_blood_sugar = max([data.blood_sugar for data in blood_sugar])
                min_blood_sugar = min([data.blood_sugar for data in blood_sugar])

                context["mean_blood_sugar"] = int(mean_blood_sugar)
                context["max_blood_sugar"] = max_blood_sugar
                context["min_blood_sugar"] = min_blood_sugar

            if len(blood_pressure) > 0:
                # mean_blood_pressure: blood pressure instances which
                mean_blood_pressure_systolic = sum(
                    [data.systolic for data in blood_pressure]
                ) / len(blood_pressure)
                mean_blood_pressure_diastolic = sum(
                    [data.diastolic for data in blood_pressure]
                ) / len(blood_pressure)
                max_blood_pressure_systolic = max(
                    [data.systolic for data in blood_pressure]
                )
                max_blood_pressure_diastolic = max(
                    [data.diastolic for data in blood_pressure]
                )
                min_blood_pressure_systolic = min(
                    [data.systolic for data in blood_pressure]
                )
                min_blood_pressure_diastolic = min(
                    [data.diastolic for data in blood_pressure]
                )
                context["mean_blood_pressure_systolic"] = int(
                    mean_blood_pressure_systolic
                )
                context["mean_blood_pressure_diastolic"] = int(
                    mean_blood_pressure_diastolic
                )
                context["max_blood_pressure_systolic"] = max_blood_pressure_systolic
                context["max_blood_pressure_diastolic"] = max_blood_pressure_diastolic
                context["min_blood_pressure_systolic"] = min_blood_pressure_systolic
                context["min_blood_pressure_diastolic"] = min_blood_pressure_diastolic

            if len(hba1c) > 0:
                context["hb1ac"] = hba1c[0].hba1c  # only one data per day

        case "diet":
            meals = Diet.objects.filter(user=request.user).prefetch_related("result")
            context["meals"] = meals

            max_calories = CustomUser.objects.get(id=request.user.id).weight * 35
            context["max_calories"] = max_calories
            context["max_carbohydrates"] = 100  # fixed value
            context["max_protein"] = int(
                CustomUser.objects.get(id=request.user.id).weight
                * 0.8  # for proteins, 0.8g per kg
            )
            context["max_fat"] = 50  # fixed value

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

            total_calories = 0
            total_carbohydrates = 0
            total_protein = 0
            total_fat = 0

            meal_calories = {}

            for meal in meals:
                food_info = meal.result.result_data["food_info"]
                meal_total_calories = sum(
                    int(food["energy_kcal"]) for food in food_info
                )
                meal_calories[meal.id] = meal_total_calories
                total_calories += sum(int(food["energy_kcal"]) for food in food_info)
                total_carbohydrates += sum(
                    int(food["carbohydrates_g"]) for food in food_info
                )
                total_protein += sum(int(food["protein_g"]) for food in food_info)
                total_fat += sum(int(food["fat_g"]) for food in food_info)

            context["total_calories"] = total_calories
            context["total_carbohydrates"] = total_carbohydrates
            context["total_protein"] = total_protein
            context["total_fat"] = total_fat
            context["meal_calories"] = meal_calories
        case "exercise":
            context["exercises"] = Exercise.objects.filter(user=request.user)
            context["total_calories"] = sum(
                [
                    exercise.exercise_calories
                    for exercise in Exercise.objects.filter(user=request.user)
                ]
            )
        case "blood":
            # get all blood related data(blood sugar, blood pressure, hba1c) and align all in one list

            blood_sugar = BloodSugar.objects.filter(user=request.user)
            blood_pressure = BloodPressure.objects.filter(user=request.user)
            hba1c = HbA1c.objects.filter(user=request.user)

            context["blood1_data"] = blood_sugar
            context["blood2_data"] = blood_pressure
            context["blood3_data"] = hba1c
        case "mypage":
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
            context["weekdays"] = ["월", "화", "수", "목", "금", "토"]
        case _:
            pass

    return render(request, template_name, context)


@login_required
def exercise_list(request):
    exercises_by_type = ExerciseType.objects.annotate(exercise_count=Count("exercise"))

    # print(exercises_by_type.values())

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


@login_required
def update_meal(request, meal_id, nutrient_name):
    """

    :param request:
    :param meal_id: target meal id
    :param nutrient_name: target nutrient name
    :return:
    """
    if request.method == "PUT":
        data = json.loads(request.body)
        name = data.get("name")
        kcal = data.get("kcal", 0)

        try:
            target_big = InferenceResult.objects.get(
                id=Diet.objects.get(id=meal_id).result_id
            )
            comma_separated = target_big.result_names_comma_separated
            if nutrient_name in comma_separated.split(","):
                comma_separated = comma_separated.replace(nutrient_name, name)
                target_big.result_names_comma_separated = comma_separated
                target_big.save()
                # TODO: Kcal update
            else:
                return JsonResponse(
                    {"success": False, "message": "Already exists"}, status=304
                )
            return JsonResponse({"success": True}, status=200)
        except Diet.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Meal not found"}, status=404
            )
    # TODO: reduce duplicate code
    elif request.method == "DELETE":
        data = json.loads(request.body)
        name = data.get("name")
        kcal = data.get("kcal", 0)

        try:
            target_big = InferenceResult.objects.get(
                id=Diet.objects.get(id=meal_id).result_id
            )
            comma_separated = target_big.result_names_comma_separated
            if len(comma_separated.split(",")) == 1:
                return JsonResponse(
                    {"success": False, "message": "마지막 음식은 삭제할 수 없습니다."},
                    status=400,
                )
            if nutrient_name in comma_separated.split(","):
                # if comma_separated == nutrient_name:
                #     comma_separated = ""
                # else:
                comma_separated = comma_separated.replace(nutrient_name + ",", "")
                target_big.result_names_comma_separated = comma_separated
                target_big.save()
            else:
                return JsonResponse(
                    {"success": False, "message": "Not found"}, status=404
                )
            return JsonResponse({"success": True}, status=200)
        except Diet.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Meal not found"}, status=404
            )
    elif request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name")
        kcal = data.get("kcal", 0)

        try:
            target_big = InferenceResult.objects.get(
                id=Diet.objects.get(id=meal_id).result_id
            )
            comma_separated = target_big.result_names_comma_separated
            comma_separated += f",{name}"
            target_big.result_names_comma_separated = comma_separated
            target_big.save()
            return JsonResponse({"success": True}, status=200)
        except Diet.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Meal not found"}, status=404
            )

    return JsonResponse(
        {"success": False, "message": "Invalid request method"}, status=400
    )


@login_required
def blood_1(request, id=None):
    if id:
        blood_sugar = BloodSugar.objects.get(id=id, user=request.user)
    else:
        blood_sugar = BloodSugar(user=request.user)

    if request.method == "POST":
        form = BloodSugarForm(request.POST, instance=blood_sugar)
        if form.is_valid():
            blood_sugar = form.save(commit=False)
            blood_sugar.user = request.user
            blood_sugar.save()
            return redirect("index")
    else:
        form = BloodSugarForm(instance=blood_sugar)
    return render(request, "users/blood_form1.html", {"form": form})


@login_required
def blood_2(request, id=None):
    if id:
        blood_pressure = BloodPressure.objects.get(id=id, user=request.user)
    else:
        blood_pressure = BloodPressure(user=request.user)

    if request.method == "POST":
        form = BloodPressureForm(request.POST, instance=blood_pressure)
        if form.is_valid():
            blood_pressure = form.save(commit=False)
            blood_pressure.user = request.user
            blood_pressure.save()
            return redirect("index")
    else:
        form = BloodPressureForm(instance=blood_pressure)
    return render(request, "users/blood_form2.html", {"form": form})


@login_required
def blood_3(request, id=None):
    if id:
        hba1c = HbA1c.objects.get(id=id, user=request.user)
    else:
        hba1c = HbA1c(user=request.user)

    if request.method == "POST":
        form = HbA1cForm(request.POST, instance=hba1c)
        if form.is_valid():
            hba1c = form.save(commit=False)
            hba1c.user = request.user
            hba1c.save()
            return redirect("index")
    else:
        form = HbA1cForm(instance=hba1c)
    return render(request, "users/blood_form3.html", {"form": form})


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
    print(fdata)
    return JsonResponse(fdata)


@login_required
def food_detail(request, id):
    meal = get_object_or_404(Diet, pk=id)
    meal.image.name = meal.image.name.split(".")[0] + "_anno.jpg"
    meal.result_names_list = meal.result.result_names_comma_separated.split(",")
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
