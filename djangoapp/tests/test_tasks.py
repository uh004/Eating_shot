# tests/test_async.py
from django.test import TestCase
from unittest.mock import patch
from ai_workload.tasks import process_inference_task


class AsyncTaskTest(TestCase):
    @patch("ai_workload.tasks.run_inference")
    def test_process_inference_task(self, mock_run_inference):
        mock_run_inference.return_value = {"result": "success"}
        process_inference_task(task_id=1)
        mock_run_inference.assert_called_once_with(task_id=1)
