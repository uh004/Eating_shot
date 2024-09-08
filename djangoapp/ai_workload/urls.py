from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.PhotoUploadView.as_view(), name="photo_upload"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
]
