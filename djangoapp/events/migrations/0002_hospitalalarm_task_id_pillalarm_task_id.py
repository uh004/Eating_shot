# Generated by Django 5.1.2 on 2024-10-12 04:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="hospitalalarm",
            name="task_id",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="pillalarm",
            name="task_id",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
