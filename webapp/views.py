from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login

from ai_workload.kafka.producer import send_inference_task
from ai_workload.models import InferenceTask
from users.models import Exercise
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


# # TODO: regenerate?, logout, change password, etc.
# @login_required
# def get_auth_token(request):
#     token, created = Token.objects.get_or_create(user=request.user)
#     return JsonResponse({'token': token.key})


#
#
#
#
#
#
#
#
#
#
#


# from django.contrib.auth.decorators import login_required
# from .models import UploadedImage
# from ai_workload.tasks import queue_inference_task
#
#
# @login_required
# def upload_image(request):
#     if request.method == "POST":
#         image = request.FILES.get("image")
#         if image:
#             # Save the uploaded image
#             uploaded_image = UploadedImage.objects.create(
#                 user=request.user, image=image
#             )
#
#             # Queue the inference task
#             queue_inference_task.delay(uploaded_image.id)
#
#             return redirect("image_status", image_id=uploaded_image.id)
#
#     return render(request, "webapp/upload.html")
#
#
# @login_required
# def image_status(request, image_id):
#     image = UploadedImage.objects.get(id=image_id)
#     return render(request, "webapp/status.html", {"image": image})


#
def load_content(request, menu):
    template_name = f"users/{menu}.html"
    return render(request, template_name)


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
def exercise_form(request):
    if request.method == "POST":
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.user = request.user
            exercise.save()
            return redirect("index")
    else:
        form = ExerciseForm()
    return render(request, "users/exercise_form.html", {"form": form})


@login_required
def exercise_list(request):
    exercises = Exercise.objects.filter(user=request.user)
    return render(request, "users/exercise_list.html", {"exercises": exercises})
