# tests/test_performance.py
from django.test import TestCase
from django.utils import timezone
from users.models import BloodSugar


class PerformanceTest(TestCase):
    def test_blood_sugar_creation_performance(self):
        start_time = timezone.now()
        for i in range(1000):
            BloodSugar.objects.create(
                user_id=1, time="morning", date="2023-01-01", blood_sugar=120
            )
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        self.assertLess(duration, 5)


# or... you can test inference task creating view(diet_form) performance
