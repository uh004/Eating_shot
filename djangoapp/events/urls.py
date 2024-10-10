from django.urls import path, include
import django_eventstream
from . import views

urlpatterns = [
    path("", include(django_eventstream.urls), {"channels": ["alarms"]}),
    path("trigger_test_alarm/", views.trigger_test_alarm, name="trigger_test_alarm"),
]
