from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import InferenceTask
from .serializers import InferenceTaskSerializer, PhotoUploadSerializer
from .kafka.producer import send_inference_task


class PhotoUploadView(generics.CreateAPIView):
    serializer_class = PhotoUploadSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        send_inference_task(task.id)
        return Response({"task_id": task.id}, status=status.HTTP_201_CREATED)


class TaskDetailView(generics.RetrieveAPIView):
    queryset = InferenceTask.objects.all()
    serializer_class = InferenceTaskSerializer
