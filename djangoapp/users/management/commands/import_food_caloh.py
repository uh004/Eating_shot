# management/commands/import_food_calories.py
import csv
from django.core.management.base import BaseCommand
from users.models import FoodCalories


class Command(BaseCommand):
    help = "Import food calories data from CSV and overwrite existing data"

    def handle(self, *args, **kwargs):
        with open("food_calories.csv", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                FoodCalories.objects.update_or_create(
                    food_name=row[0],
                    defaults={
                        "energy_kcal": int(row[1]),
                        "weight_g": int(row[2]),
                        "carbohydrates_g": float(row[3]),
                        "protein_g": float(row[4]),
                        "fat_g": float(row[5]),
                        "diabetes_risk_classification": int(row[6]),
                        "label": int(row[7]),
                    },
                )
        self.stdout.write(self.style.SUCCESS("Successfully imported and updated data"))
