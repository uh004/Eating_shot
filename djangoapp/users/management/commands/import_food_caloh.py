# management/commands/import_food_calories.py
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from users.models import FoodCalories


class Command(BaseCommand):
    help = "Import food calories data from inference server and overwrite existing data"

    def handle(self, *args, **kwargs):
        try:
            response = requests.get(f"{settings.INFERENCE_SERVER_URL}/nutrition_data")
            response.raise_for_status()
            nutrition_data = response.json()

            for item in nutrition_data:
                FoodCalories.objects.update_or_create(
                    food_name=item["음식명"],
                    defaults={
                        "energy_kcal": int(float(item["에너지(kcal)"])),
                        "weight_g": int(float(item["중량(g)"]))
                        if item["중량(g)"]
                        else 0,  # TODO: fill in the missing values in the csv later
                        "carbohydrates_g": float(item["탄수화물(g)"]),
                        "protein_g": float(item["단백질(g)"]),
                        "fat_g": float(item["지방(g)"]),
                        "diabetes_risk_classification": int(item["당뇨 위험 분류"]),
                        # "label": int(item["레이블"]),
                        "is_meat": int(float(item["고기"])),
                        "is_veg": int(float(item["채소"])),
                        "is_seafood": int(float(item["해산물"])),
                    },
                )
            self.stdout.write(
                self.style.SUCCESS("Successfully imported and updated data")
            )
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to fetch data from inference server: {str(e)}"
                )
            )
