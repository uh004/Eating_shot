# Generated by Django 5.1.2 on 2024-10-17 23:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ai_workload", "0003_inferenceresult_modified_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="inferenceresult",
            name="result_changeable_food_info",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
