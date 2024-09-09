# tests/test_security.py
from django.test import TestCase
from rest_framework.test import APIClient


class SecurityTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthorized_access(self):
        response = self.client.get("/api/v1/inference-tasks/")
        self.assertEqual(
            response.status_code, 403
        )  # unauthorized access should return 403
