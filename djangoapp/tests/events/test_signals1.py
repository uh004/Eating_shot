from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch
from events.models import PillAlarm, HospitalAlarm
from events.signals import (
    pill_alarm_post_save,
    hospital_alarm_post_save,
    schedule_pill_alarm,
    schedule_hospital_alarm,
)
from users.models import CustomUser
from django.db.models.signals import post_save


class AlarmSignalTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="12345", email="craftguy55+sub@gmail.com"
        )
        # Disconnect signals to avoid multiple connections during testing
        post_save.disconnect(pill_alarm_post_save, sender=PillAlarm)
        post_save.disconnect(hospital_alarm_post_save, sender=HospitalAlarm)

    def tearDown(self):
        # Reconnect signals after each test
        post_save.connect(pill_alarm_post_save, sender=PillAlarm)
        post_save.connect(hospital_alarm_post_save, sender=HospitalAlarm)

    @patch("events.signals.trigger_alarm_task.apply_async")
    def test_schedule_pill_alarm(self, mock_apply_async):
        alarm_time = (timezone.localtime() + timedelta(seconds=1)).time()
        alarm = PillAlarm.objects.create(
            time=alarm_time, weekday="MON,TUE", user_id=self.user.id
        )
        schedule_pill_alarm(alarm)
        self.assertEqual(mock_apply_async.call_count, 2)  # Two weekdays

    @patch("events.signals.trigger_alarm_task.apply_async")
    def test_schedule_hospital_alarm(self, mock_apply_async):
        alarm_time = (timezone.localtime() + timedelta(seconds=1)).time()
        alarm = HospitalAlarm.objects.create(
            hospital_date=timezone.now().date(),
            hospital_time=alarm_time,
            user_id=self.user.id,
        )
        schedule_hospital_alarm(alarm)
        self.assertEqual(mock_apply_async.call_count, 1)

    # @patch("events.signals.trigger_alarm_task.apply_async")
    # def test_reschedule_alarms(self, mock_apply_async):
    #     alarm_time = (timezone.now() + timedelta(seconds=1)).time()
    #     PillAlarm.objects.create(
    #         time=alarm_time, weekday="MON,TUE", user_id=self.user.id
    #     )
    #     HospitalAlarm.objects.create(
    #         hospital_date=timezone.now().date(),
    #         hospital_time=alarm_time,
    #         user_id=self.user.id,
    #     )
    #     reschedule_alarms(None)
    #     self.assertEqual(mock_apply_async.call_count, 2)  # One for each alarm
