from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="api_register"),
    path("login/", LoginAPIView.as_view(), name="api_login"),
    path("logout/", LogoutAPIView.as_view(), name="api_logout"),
    ##
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
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
