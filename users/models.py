# users/models.py
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female")],
        null=True,
        blank=True,
    )
    goal = models.CharField(
        max_length=20,
        choices=[
            ("chronic_disease", "만성질환"),
            ("healthy_diet", "건강한 식습관, 체중 감량"),
        ],
        null=True,
        blank=True,
    )
    health_conditions = models.CharField(max_length=255, null=True, blank=True)


class BloodSugar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time = models.CharField(max_length=20)
    date = models.DateField()
    blood_sugar = models.IntegerField()


class BloodPressure(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    systolic = models.IntegerField()
    diastolic = models.IntegerField()


class HbA1c(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hba1c = models.FloatField()
    hba1c_time = models.DateField()


class Diet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=10)
    date = models.DateField()
    image = models.ImageField(upload_to="inference_photos/")
    result = models.ForeignKey(
        "ai_workload.InferenceResult", on_delete=models.SET_NULL, null=True, blank=True
    )


class Exercise(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise_time = models.IntegerField()
    date = models.DateField()
    intensity = models.CharField(max_length=10)
