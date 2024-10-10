from django.db import models
from django.conf import settings

# Create your models here.


class PillAlarm(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pill_name = models.CharField(max_length=50)
    weekday = models.CharField(max_length=50)
    time = models.TimeField()


class HospitalAlarm(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=50)
    hospital_date = models.DateField()
    hospital_time = models.TimeField()
