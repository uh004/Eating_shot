from django.urls import path, include

urlpatterns = [
    path("auth/", include("users.urls")),
    path("ai_workload/", include("ai_workload.urls")),
]
