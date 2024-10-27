from django.conf.urls.static import static
from django.urls import path, re_path, include
from core import settings
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("", include("pwa.urls")),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("change_password/", views.change_password, name="change_password"),
    path("post-enrollment/", views.info_view, name="info"),
    path("load_content/<str:menu>/", views.load_content, name="load_content"),
    path(
        "blood_form/<str:data_type>/<int:id>/", views.blood_data_view, name="blood_form"
    ),
    path("blood_form/<str:data_type>/", views.blood_data_view, name="blood_form"),
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
        "mod/<int:meal_id>/<str:existing_food_name>/",
        views.update_meal,
        name="update_meal",
    ),
    path("food-detail/<int:id>", views.food_detail, name="food_detail"),
    path("pill-alarm/", views.pill_alarm, name="pill_alarm"),
    path("pill-alarm/<int:id>", views.pill_alarm, name="pill_alarm"),
    path("hospital-alarm/", views.hospital_alarm, name="hospital_alarm"),
    path("hospital-alarm/<int:id>", views.hospital_alarm, name="hospital_alarm"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root="./photos")
