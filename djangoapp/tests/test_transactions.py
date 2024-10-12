# events/test_transactions.py
from django.db import transaction
from django.test import TestCase
from users.models import BloodSugar


class TransactionTest(TestCase):
    def test_atomic_transaction(self):
        try:
            with transaction.atomic():
                BloodSugar.objects.create(
                    user_id=1, time="morning", date="2023-01-01", blood_sugar=120
                )
                raise Exception("Forced exception")
        except Exception:
            pass
        self.assertEqual(BloodSugar.objects.count(), 0)
