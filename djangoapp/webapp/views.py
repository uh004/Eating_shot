from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout

from ai_workload.kafka.producer import send_inference_task
from ai_workload.models import InferenceTask
from users.models import Exercise, Diet, ExerciseType, BloodSugar, BloodPressure, HbA1c
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    HealthInfoForm,
    BloodSugarForm,
    BloodPressureForm,
    HbA1cForm,
    ExerciseForm,
    DietForm,
)


@login_required
def index(request):
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
            if (
                user.height is None
            ):  # check for any required fields present in the user model (e.g. height)
                return redirect("info")
            else:
                return redirect("index")
        else:
            # TODO: show error message
            return render(request, "users/login.html", {"form": form})
    else:
        form = CustomAuthenticationForm()
    return render(request, "users/login.html", {"form": form})


@login_required
def info_view(request):
    if request.method == "POST":
        form = HealthInfoForm(request.POST)
        if form.is_valid():
            user = request.user
            user.height = form.cleaned_data["height"]
            user.weight = form.cleaned_data["weight"]
            user.age = form.cleaned_data["age"]
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


#
def load_content(request, menu):
    pages = ["diet", "exercise", "blood", "report", "mypage"]
    template_name = f"users/{menu}.html"

    context = {}

    match menu:
        case "diet":
            context["meals"] = Diet.objects.filter(user=request.user)
        case "exercise":
            context["exercises"] = Exercise.objects.filter(user=request.user)
        case "blood":
            # get all blood related data(blood sugar, blood pressure, hba1c) and align all in one list

            blood_sugar = BloodSugar.objects.filter(user=request.user)
            blood_pressure = BloodPressure.objects.filter(user=request.user)
            hba1c = HbA1c.objects.filter(user=request.user)

            context["blood1_data"] = blood_sugar
            context["blood2_data"] = blood_pressure
            context["blood3_data"] = hba1c
        case "report":
            pass
            # 주간, 일간

            # 총 섭취 n kcal(탄, 단, 지)
            # 총 소모 n kcal
            # 총 운동시간 n 분
            # 당뇨지표(top 3가 혈당이 가장 높아요!) -> 혈압, 당화혈색소, 현재 당신의 상태는 <> 입니다.
        case "mypage":
            user_info = request.user
            context["user_info"] = user_info
            conversion_table = {  # TODO: use i18n instead of hardcoding
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
        case _:
            pass

    return render(request, template_name, context)


@login_required
def exercise_list(request):
    exercises_by_type = ExerciseType.objects.annotate(exercise_count=Count("exercise"))

    print(exercises_by_type.values())

    return render(
        request,
        "users/exercise_list.html",
        {"exercises_by_type": exercises_by_type},
    )


@login_required
def diet_form(request):
    if request.method == "POST":
        form = DietForm(request.POST, request.FILES)
        if form.is_valid():
            diet = form.save(commit=False)
            diet.user = request.user
            diet.save()

            # Create an InferenceTask instance
            inference_task = InferenceTask.objects.create(
                user=request.user, photo=diet.image, status="PENDING"
            )

            # Queue the inference task
            send_inference_task(inference_task.id)

            return redirect("index")
    else:
        form = DietForm()
    return render(request, "users/diet_form.html", {"form": form})

# 새로 식단 수정 폼 추가함
@login_required
def diet_revise_form(request):
    if request.method == "POST":
        form = DietForm(request.POST, request.FILES)
        if form.is_valid():
            diet = form.save(commit=False)
            diet.user = request.user
            diet.save()

            # Create an InferenceTask instance
            inference_task = InferenceTask.objects.create(
                user=request.user, photo=diet.image, status="PENDING"
            )

            # Queue the inference task
            send_inference_task(inference_task.id)

            return redirect("index")
    else:
        form = DietForm()
    return render(request, "users/diet_revise_form.html", {"form": form})

@login_required
def blood_1(request):
    if request.method == "POST":
        form = BloodSugarForm(request.POST)
        if form.is_valid():
            blood_sugar = form.save(commit=False)
            blood_sugar.user = request.user
            blood_sugar.save()
            return redirect("index")
    else:
        form = BloodSugarForm()
    return render(request, "users/blood_form1.html", {"form": form})


@login_required
def blood_2(request):
    if request.method == "POST":
        form = BloodPressureForm(request.POST)
        if form.is_valid():
            blood_pressure = form.save(commit=False)
            blood_pressure.user = request.user
            blood_pressure.save()
            return redirect("index")
    else:
        form = BloodPressureForm()
    return render(request, "users/blood_form2.html", {"form": form})


@login_required
def blood_3(request):
    if request.method == "POST":
        form = HbA1cForm(request.POST)
        if form.is_valid():
            hba1c = form.save(commit=False)
            hba1c.user = request.user
            hba1c.save()
            return redirect("index")
    else:
        form = HbA1cForm()
    return render(request, "users/blood_form3.html", {"form": form})


@login_required
def exercise_form(request, exercise_id):
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.user = request.user
            exercise.exercise_type = ExerciseType.objects.get(id=exercise_id)
            exercise.save()
            return redirect("index")
    else:
        form = ExerciseForm()
    return render(
        request,
        "users/exercise_form.html",
        {
            "form": form,
            "exercise_name": ExerciseType.objects.get(id=exercise_id).name,
            "calories_per_hour": ExerciseType.objects.get(
                id=exercise_id
            ).calories_per_hour,
        },
    )

def exercise_revise_form(request):
    return render(request, "users/exercise_revise_form.html", {})

def blood1_revise_form(request):
    return render(request, "users/blood1_revise_form.html", {})

def blood2_revise_form(request):
    return render(request, "users/blood2_revise_form.html", {})

def blood3_revise_form(request):
    return render(request, "users/blood3_revise_form.html", {})