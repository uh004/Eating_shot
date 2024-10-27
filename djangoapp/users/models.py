# users/models.py
import os

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from datetime import date

from django_resized import ResizedImageField


def diet_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<id>/<filename>
    # print(instance.user.id)
    return os.path.join(str(instance.user.id), filename)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=True)
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

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        if self.birthdate:
            today = date.today()
            self.age = (
                today.year
                - self.birthdate.year
                - (
                    (today.month, today.day)
                    < (self.birthdate.month, self.birthdate.day)
                )
            )
        super(CustomUser, self).save(*args, **kwargs)


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
    date = models.DateField()


class Diet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=10)
    date = models.DateField()
    # image = models.ImageField(upload_to=diet_image_path)
    image = ResizedImageField(size=[640, 640], upload_to=diet_image_path)
    result = models.ForeignKey(
        "ai_workload.InferenceResult", on_delete=models.SET_NULL, null=True, blank=True
    )

    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         # Save the instance to generate an ID
    #         temp_image = self.image
    #         self.image = None
    #         super().save(*args, **kwargs)
    #         self.image = temp_image
    #     # Now that the instance has an ID, save again to update the image path
    #     super().save(*args, **kwargs)


class ExerciseType(models.Model):
    name = models.CharField(max_length=50)
    calories_per_hour = models.IntegerField()
    exercise_category = models.CharField(
        max_length=10,
        choices=[("aerobic", "유산소"), ("anaerobic", "무산소")],
        null=True,
    )

    def __str__(self):
        return self.name


class Exercise(models.Model):
    # look at the migration file to see the exercise types

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise_time = models.IntegerField()
    exercise_calories = models.IntegerField()
    exercise_type = models.ForeignKey(ExerciseType, on_delete=models.CASCADE)
    date = models.DateField()
    intensity = models.CharField(max_length=10)

    def calculate_calories(self):
        return (self.exercise_type.calories_per_hour / 60) * self.exercise_time

    def save(self, *args, **kwargs):
        self.exercise_calories = self.calculate_calories()
        super().save(*args, **kwargs)

    # @classmethod
    # def get_exercise_types(cls):
    #     return [exercise[2] for exercise in cls.exercise_types]


class FoodCalories(models.Model):
    food_name = models.CharField(max_length=100)
    energy_kcal = models.IntegerField()
    weight_g = models.IntegerField()
    carbohydrates_g = models.FloatField()
    protein_g = models.FloatField()
    fat_g = models.FloatField()
    diabetes_risk_classification = models.IntegerField()
    is_meat = models.FloatField()
    is_veg = models.FloatField()
    is_seafood = models.FloatField()

    def __str__(self):
        return self.food_name
