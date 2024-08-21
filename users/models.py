# users/models.py
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


# class SomeModel(models.Model)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     pass
