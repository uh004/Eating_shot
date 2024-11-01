import logging
from datetime import datetime, timedelta

from celery import current_app
from celery.result import AsyncResult
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import HospitalAlarm, PillAlarm
from .tasks import alarm_callback_task, reschedule_pill_alarm, trigger_alarm_task

WEEKDAY_CONVERSION = {
    "MON": 0,
    "TUE": 1,
    "WED": 2,
    "THU": 3,
    "FRI": 4,
    "SAT": 5,
    "SUN": 6,
}

logger = logging.getLogger(__name__)


def schedule_pill_alarm(alarm):
    """
    Schedule a pill alarm

    :param alarm:
    :return:
    """
    logger.debug(f"Scheduling pill alarm for {alarm}")
    # now = timezone.now() # dont use timezone.now() because it's not timezone aware
    now = timezone.localtime()
    weekdays = alarm.weekday.split(",")
    alarm_time = datetime.combine(now.date(), alarm.time)
    alarm_time = timezone.make_aware(alarm_time, timezone.get_current_timezone())

    task_ids = {}

    for weekday in weekdays:
        weekday_num = WEEKDAY_CONVERSION[weekday.upper()]
        days_ahead = (
            weekday_num - now.weekday() + 7
        ) % 7  # Calculate days until next weekday (0-6)
        if (
            days_ahead == 0 and alarm_time < now
        ):  # If the alarm time has already passed today
            days_ahead = 7  # Schedule for next week
        next_alarm_time = alarm_time + timedelta(
            days=days_ahead
        )  # Calculate the next alarm time
        time_to_wait = (
            next_alarm_time - now
        ).total_seconds()  # Calculate the time to wait in seconds
        logger.debug(
            f"Scheduling alarm for {next_alarm_time} with countdown {time_to_wait}"
        )
        task = trigger_alarm_task.apply_async(
            (alarm.user_id, "pill", alarm.id, "Pill Alarm: It's time!"),
            countdown=time_to_wait - 1,  # currently using countdown instead of eta
            link=alarm_callback_task.s(
                alarm.user_id, "pill", alarm.id
            ),  # Callback task
        )
        task_ids[weekday] = task.id  # Save the task id for the weekday

    alarm.task_ids = task_ids
    alarm.save()

    # Schedule the reschedule task for the next week
    reschedule_time = now + timedelta(weeks=1)
    reschedule_task = reschedule_pill_alarm.apply_async(
        (alarm.id,), eta=reschedule_time
    )
    alarm.reschedule_task_id = reschedule_task.id
    alarm.save()


def schedule_hospital_alarm(alarm):
    """
    Schedule a hospital alarm

    :param alarm:
    :return:
    """
    logger.debug(f"Scheduling hospital alarm for {alarm}")
    now = (
        timezone.localtime()
    )  # dont use timezone.now() because it's not timezone aware
    alarm_datetime = datetime.combine(alarm.hospital_date, alarm.hospital_time)
    alarm_datetime = timezone.make_aware(
        alarm_datetime, timezone.get_current_timezone()
    )
    if alarm_datetime >= now:
        time_to_wait = (alarm_datetime - now).total_seconds()
        logger.debug(
            f"Scheduling alarm for {alarm_datetime} with countdown {time_to_wait}"
        )
        task = trigger_alarm_task.apply_async(
            (
                alarm.user_id,
                "hospital",
                alarm.id,
                "Hospital Appointment Alarm: It's time!",
            ),
            countdown=time_to_wait - 1,  # currently using countdown instead of eta
            link=alarm_callback_task.s(
                alarm.user_id, "hospital", alarm.id
            ),  # Callback task
        )
        alarm.task_id = task.id
        alarm.save()


# UNUSED UNUSED
# @receiver(post_migrate)
# def reschedule_alarms(sender, **kwargs):
#     now = timezone.now()
#
#     # Get all future alarms that were not triggered
#     pending_pill_alarms = PillAlarm.objects.filter(time__gte=now)
#     for alarm in pending_pill_alarms:
#         schedule_pill_alarm(alarm)
#
#     pending_hospital_alarms = HospitalAlarm.objects.filter(
#         hospital_date__gte=now.date(), hospital_time__gte=now.time()
#     )
#     for alarm in pending_hospital_alarms:
#         schedule_hospital_alarm(alarm)


@receiver(post_save, sender=PillAlarm)
def pill_alarm_post_save(sender, instance, created, **kwargs):
    """
    this function is called when a new PillAlarm is created
    """
    if created:
        schedule_pill_alarm(instance)


@receiver(post_save, sender=HospitalAlarm)
def hospital_alarm_post_save(sender, instance, created, **kwargs):
    """
    this function is called when a new HospitalAlarm is created
    """
    if created:
        schedule_hospital_alarm(instance)


@receiver(post_delete, sender=PillAlarm)
def pill_alarm_post_delete(sender, instance, **kwargs):
    """
    this function is called when a PillAlarm is deleted
    """
    if instance.id:
        for task_id in instance.task_ids.values():
            print(f"Revoking task {task_id}")
            task_result = AsyncResult(task_id)
            current_app.control.revoke(task_id, terminate=True)
            task_result.forget()
        if instance.reschedule_task_id:
            print(f"Revoking task {instance.reschedule_task_id}")
            task_result = AsyncResult(instance.reschedule_task_id)
            current_app.control.revoke(instance.reschedule_task_id, terminate=True)
            task_result.forget()


@receiver(post_delete, sender=HospitalAlarm)
def hospital_alarm_post_delete(sender, instance, **kwargs):
    """
    this function is called when a HospitalAlarm is deleted
    """

    if instance.id:
        print(f"Revoking task {instance.task_id}")
        task_result = AsyncResult(instance.task_id)
        current_app.control.revoke(instance.task_id, terminate=True)
        task_result.forget()
