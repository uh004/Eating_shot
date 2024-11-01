from django.urls import include, path

urlpatterns = [
    path("auth/", include("users.urls")),
    path("ai_workload/", include("ai_workload.urls")),
]
