from django.db.models.signals import post_save
from django.dispatch import receiver
from django_eventstream import send_event
from .models import PillAlarm, HospitalAlarm


@receiver(post_save, sender=PillAlarm)
def pill_alarm_created(sender, instance, created, **kwargs):
    if created:
        send_event(
            "alarms",
            "pill_alarm",
            {
                "user_id": instance.user.id,
                "pill_name": instance.pill_name,
                "weekday": instance.weekday,
                "time": instance.time.strftime("%H:%M"),
            },
        )


@receiver(post_save, sender=HospitalAlarm)
def hospital_alarm_created(sender, instance, created, **kwargs):
    if created:
        send_event(
            "alarms",
            "hospital_alarm",
            {
                "user_id": instance.user.id,
                "hospital_name": instance.hospital_name,
                "date": instance.hospital_date.isoformat(),
                "time": instance.hospital_time.strftime("%H:%M"),
            },
        )
