from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("post-enrollment/", views.info_view, name="info"),
    path("load_content/<str:menu>/", views.load_content, name="load_content"),
    path("blood1/", views.blood_1, name="blood1"),
    path("blood2/", views.blood_2, name="blood2"),
    path("blood3/", views.blood_3, name="blood3"),
    path("diet-form/", views.diet_form, name="diet_form"),
    path("exercise_form/<int:exercise_id>/", views.exercise_form, name="exercise_form"),
    path("exercise-list/", views.exercise_list, name="exercise_list"),
    path("logout/", views.logout_view, name="logout"),
]
