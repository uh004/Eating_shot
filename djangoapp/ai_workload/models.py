import os

from django.conf import settings
from django.db import models


# from django.conf import settings
# from django.contrib.auth import get_user_model

# User = get_user_model()
# def diet_image_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/<id>/<filename>
#     return os.path.join(instance.id, filename)
# TODO: upload path for this situation

class InferenceTask(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="uploads") # TODO: upload path for this situation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    result = models.OneToOneField(
        "InferenceResult",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task",
    )


class InferenceResult(models.Model):
    # task = models.OneToOneField(
    #     "InferenceTask", on_delete=models.CASCADE, related_name="result"
    # )
    result_data = models.JSONField()
    result_names_comma_separated = models.TextField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
