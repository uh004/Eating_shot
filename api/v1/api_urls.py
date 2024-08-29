from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    UserProfileAPIView,
    # RequestPasswordResetAPIView,
    # ResetPasswordAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="api_register"),
    path("login/", LoginAPIView.as_view(), name="api_login"),
    path("logout/", LogoutAPIView.as_view(), name="api_logout"),
    ##
    path("token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
    path("profile/", UserProfileAPIView.as_view(), name="api_profile"),
    # path(
    #     "change-password/", ChangePasswordAPIView.as_view(), name="api_change_password"
    # ),
    # path(
    #     "request-password-reset/",
    #     RequestPasswordResetAPIView.as_view(),
    #     name="api_request_password_reset",
    # ),
    # path(
    #     "reset-password/<uidb64>/<token>/",
    #     ResetPasswordAPIView.as_view(),
    #     name="api_reset_password",
    # ),
]
