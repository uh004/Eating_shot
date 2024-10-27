from django.conf import settings
from django.db import models

# from django.conf import settings
# from django.contrib.auth import get_user_model

# User = get_user_model()
# def diet_image_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/<id>/<filename>
#     return os.path.join(instance.id, filename)
# TODO: upload path for this situation


class InferenceTask(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(
        upload_to="uploads"
    )  # TODO: upload path for this situation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    result = models.OneToOneField(
        "InferenceResult",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task",
    )


class InferenceResult(models.Model):
    # task = models.OneToOneField(
    #     "InferenceTask", on_delete=models.CASCADE, related_name="result"
    # )
    result_data = models.JSONField()  # the raw result from the first inference
    result_changeable_food_info = models.JSONField(
        null=True, blank=True
    )  # the food info that can be changed by the user
    result_names_comma_separated = models.TextField(
        max_length=100, blank=True
    )  # the names of the food items in food_info
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # This is a new instance
            self.initialize_changeable_food_info()
            self.result_names_comma_separated = ",".join(
                [pred["name"] for pred in self.result_data["predictions"]]
            )

        if self.result_changeable_food_info:
            self.result_names_comma_separated = ",".join(
                [
                    pred["food_name"]
                    for pred in self.result_changeable_food_info
                    if pred["food_name"] != "TOTAL"
                ]
            )

        super().save(*args, **kwargs)
        self.update_nutrition_data()

    def initialize_changeable_food_info(self):
        if "food_info" in self.result_data:
            self.result_changeable_food_info = self.result_data["food_info"]

    def update_nutrition_data(self):
        nutrition_totals = {
            "energy_kcal": 0,
            "weight_g": 0,
            "carbohydrates_g": 0,
            "protein_g": 0,
            "fat_g": 0,
            # "diabetes_risk_classification": 0,
            "is_meat": 0,
            "is_veg": 0,
            "is_seafood": 0,
        }

        temp = [
            x for x in self.result_changeable_food_info if x["food_name"] != "TOTAL"
        ]

        for food_item in temp:
            for key in nutrition_totals.keys():
                nutrition_totals[key] += int(food_item.get(key, 0))

        temp.append(
            {"food_name": "TOTAL", **{k: str(v) for k, v in nutrition_totals.items()}}
        )

        self.result_changeable_food_info = temp

        super().save(update_fields=["result_changeable_food_info"])
