import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.update(
    task_acks_late=True,  # allows for tasks to be acknowledged later (to revoke tasks)
)

app.autodiscover_tasks()
