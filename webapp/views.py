from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CustomAuthenticationForm, HealthInfoForm


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
            return redirect("info")
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
