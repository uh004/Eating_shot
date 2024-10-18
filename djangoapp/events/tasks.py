from celery import shared_task
from django.core.management import call_command
from django.db import connection
import logging
from django_eventstream import send_event
from .models import PillAlarm, HospitalAlarm
from celery import current_app
from celery.result import AsyncResult
from celery.contrib.abortable import AbortableTask

logger = logging.getLogger(__name__)


def send_sse_event(user_id, alarm_type, alarm_id, message):
    """
    Send an SSE event to the user at the specified channel 'alarms_{user_id}'

    :param user_id:
    :param alarm_type:
    :param alarm_id:
    :param message:
    :return:
    """
    try:
        logger.info(
            f"Attempting to send SSE event for {alarm_type} with id {alarm_id} to user {user_id}"
        )
        channel_name = f"alarms_{user_id}"
        send_event(
            channel_name,
            "message",
            {"type": alarm_type, "id": alarm_id, "message": message},
        )
        logger.info(
            f"SSE event sent successfully for {alarm_type} with id {alarm_id} to user {user_id}"
        )
    except Exception as e:
        logger.error(f"Failed to send SSE event: {str(e)}")


@shared_task(base=AbortableTask)
def trigger_alarm_task(user_id, alarm_type, alarm_id, message):
    """
    Task to trigger an alarm reminder

    :param user_id:
    :param alarm_type:
    :param alarm_id:
    :param message:
    """
    if trigger_alarm_task.is_aborted():
        print(f"Task for {alarm_type} with id {alarm_id} for user {user_id} aborted")
        return
    print(f"Triggering alarm for {alarm_type} with id {alarm_id} for user {user_id}")

    connection.close()

    send_sse_event(user_id, alarm_type, alarm_id, message)


@shared_task
def alarm_callback_task(result, user_id, alarm_type, alarm_id):
    """
    Callback function for alarm tasks that have completed

    deletes done tasks from the task_ids dictionary of the alarm

    :param user_id:
    :param alarm_type:
    :param alarm_id:
    """
    print(f"Callback for alarm {alarm_type} with id {alarm_id} for user {user_id}")
    if alarm_type == "pill":
        alarm = PillAlarm.objects.get(id=alarm_id)
        task_ids = alarm.task_ids
        for weekday, task_id in list(task_ids.items()):
            task_result = AsyncResult(task_id)
            if task_result.status == "SUCCESS":
                del task_ids[weekday]
                print(f"Task {task_id} completed successfully")

        if not task_ids:
            alarm.delete()
        else:
            alarm.task_ids = task_ids
            alarm.save()
    elif alarm_type == "hospital":
        alarm = HospitalAlarm.objects.get(id=alarm_id)
        current_app.control.revoke(alarm.task_id, terminate=True)
        alarm.delete()


@shared_task(base=AbortableTask)
def reschedule_pill_alarm(alarm_id):
    """
    Reschedule a 'pill' alarm

    :param alarm_id:
    """
    if reschedule_pill_alarm.is_aborted():
        print(f"Reschedule task for pill alarm with id {alarm_id} aborted")
        return
    alarm = PillAlarm.objects.get(id=alarm_id)

    from .signals import schedule_pill_alarm

    schedule_pill_alarm(alarm)


# # command to clean past alarms and revoke associated Celery tasks
# def clean_past_alarms():
#     now = timezone.localtime()
#
#     # Revoke and delete past PillAlarms
#     past_pill_alarms = PillAlarm.objects.filter(time__lt=now)
#     for alarm in past_pill_alarms:
#         for task_id in alarm.task_ids.values():
#             current_app.control.revoke(task_id, terminate=True)
#     past_pill_alarms.delete()
#
#     # Revoke and delete past HospitalAlarms
#     past_hospital_alarms = HospitalAlarm.objects.filter(hospital_date__lt=now.date())
#     for alarm in past_hospital_alarms:
#         if alarm.task_id:
#             current_app.control.revoke(alarm.task_id, terminate=True)
#     past_hospital_alarms.delete()


def purge_all_tasks():
    """
    Purge all tasks from the default queue

    equivalent to: celery -A core purge
    """
    try:
        num_purged = current_app.control.purge()
        print(f"Purged {num_purged} tasks from the default queue.")
    except Exception as e:
        print(f"Failed to purge tasks: {str(e)}")


def clean_disassociated_tasks():
    """
    Clean up tasks that are not associated with any alarms
    """
    pill_alarm = PillAlarm.objects.all()
    hospital_alarm = HospitalAlarm.objects.all()
    if not pill_alarm and not hospital_alarm:
        purge_all_tasks()
        return

    tasks = current_app.control.inspect().scheduled().keys()

    for task in tasks:
        if (
            task not in pill_alarm.task_ids.values()
            and task not in hospital_alarm.task_id
        ):
            current_app.control.revoke(task, terminate=True)
            print(f"Revoked task {task}")


# move this task somewhere else?
@shared_task
def sync_nutrition_data():
    call_command("import_food_calories")
