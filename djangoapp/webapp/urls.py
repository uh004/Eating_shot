from django.conf.urls.static import static
from django.urls import path, re_path
from core import settings
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("post-enrollment/", views.info_view, name="info"),
    path("load_content/<str:menu>/", views.load_content, name="load_content"),
    path("blood1/", views.blood_1, name="blood1"),
    path("blood1/<int:id>/", views.blood_1, name="blood1_edit"),
    path("blood2/", views.blood_2, name="blood2"),
    path("blood2/<int:id>/", views.blood_2, name="blood2_edit"),
    path("blood3/", views.blood_3, name="blood3"),
    path("blood3/<int:id>/", views.blood_3, name="blood3_edit"),
    path("diet-form/", views.diet_form, name="diet_form"),
    path("diet-form/<int:id>/", views.diet_form, name="diet_form_edit"),
    re_path(
        r"^exercise-form/(?P<exercise_type_id>\d+)/(?P<exercise_id>[^/]+)?/$",
        views.exercise_form,
        name="exercise_form",
    ),
    path("exercise-list/", views.exercise_list, name="exercise_list"),
    path("mypage-revise-form/", views.mypage_revise_form, name="mypage_revise_form"),
    path(
        "get_chart_data/<str:chart_type>/<str:detail_type>",
        views.get_chart_data,
        name="get_chart_data",
    ),
    path("delete/<str:menu>/<int:id>/", views.delete_request, name="delete"),
    path(
        "mod/<int:meal_id>/<str:nutrient_name>/",
        views.update_meal,
        name="update_meal",
    ),
    path("food-detail/<int:id>", views.food_detail, name="food_detail"),
    path("pill-alarm/", views.pill_alarm, name="pill_alarm"),
    path("hospital-alarm/", views.hospital_alarm, name="hospital_alarm")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root="../photos")
