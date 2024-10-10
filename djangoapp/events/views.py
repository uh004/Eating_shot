from django.http import HttpResponse
from django_eventstream import send_event
from django.contrib.auth.decorators import login_required


@login_required
def trigger_test_alarm(request):
    send_event("alarms", "test_alarm", {"message": "This is a test alarm!"})
    return HttpResponse("Test alarm sent!")
