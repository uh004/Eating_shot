import django_eventstream
from django.urls import include, path

from . import views

urlpatterns = [
    path("", include(django_eventstream.urls)),
    path("trigger_test_alarm/", views.trigger_test_alarm, name="trigger_test_alarm"),
]
