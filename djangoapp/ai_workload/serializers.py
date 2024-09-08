from rest_framework import serializers
from .models import InferenceTask, InferenceResult


class InferenceResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InferenceResult
        fields = ["result_data", "created_at"]


class InferenceTaskSerializer(serializers.ModelSerializer):
    result = InferenceResultSerializer(read_only=True)

    class Meta:
        model = InferenceTask
        fields = ["id", "user", "photo", "status", "created_at", "updated_at", "result"]


class PhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InferenceTask
        fields = ["user", "photo"]
