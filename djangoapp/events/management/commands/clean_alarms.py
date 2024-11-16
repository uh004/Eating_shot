from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import HospitalAlarm, PillAlarm
from events.tasks import clean_disassociated_tasks


class Command(BaseCommand):
    help = "Clean past alarms"

    def handle(self, *args, **kwargs):
        now = timezone.localtime()
        PillAlarm.objects.filter(time__lt=now).delete()
        HospitalAlarm.objects.filter(hospital_date__lt=now.date()).delete()
        self.stdout.write(self.style.SUCCESS("Successfully cleaned past alarms"))
        clean_disassociated_tasks()
        self.stdout.write(
            self.style.SUCCESS("Successfully cleaned disassociated Celery tasks")
        )
