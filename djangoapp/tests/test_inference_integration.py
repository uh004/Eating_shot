# events/test_integration.py
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import CustomUser


class InferenceIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", password="12345"
        )
        self.client.login(username="testuser", password="12345")

    def test_inference_task_creation_and_retrieval(self):
        # Create an inference task
        response = self.client.post("/api/v1/inference-tasks/", {"data": "test data"})
        self.assertEqual(response.status_code, 201)
        task_id = response.data["id"]

        # Retrieve the created task
        response = self.client.get(f"/api/v1/inference-tasks/{task_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"], "test data")
