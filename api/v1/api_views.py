from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    CustomUserSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
)

CustomUser = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


# just use pyjwt and dont use 3rd party libs like rest_framework_simplejwt?? no. this is more convenient
class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            print(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class RequestPasswordResetAPIView(generics.GenericAPIView):
#     serializer_class = ResetPasswordSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data["email"]
#             user = CustomUser.objects.filter(email=email).first()
#             if user:
#                 token = default_token_generator.make_token(user)
#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 reset_link = f"https://yourfrontend.com/reset-password/{uid}/{token}/"
#                 send_mail(
#                     "Password Reset",
#                     f"Use this link to reset your password: {reset_link}",
#                     "from@example.com",
#                     [email],
#                     fail_silently=False,
#                 )
#             return Response(
#                 {"message": "Password reset email sent if user exists"},
#                 status=status.HTTP_200_OK,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class ResetPasswordAPIView(generics.GenericAPIView):
#     serializer_class = ResetPasswordSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def post(self, request, uidb64, token):
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = CustomUser.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
#             user = None
#
#         if user is not None and default_token_generator.check_token(user, token):
#             serializer = self.get_serializer(data=request.data)
#             if serializer.is_valid():
#                 user.set_password(serializer.validated_data["new_password"])
#                 user.save()
#                 return Response(
#                     {"message": "Password has been reset"}, status=status.HTTP_200_OK
#                 )
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(
#             {"message": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST
#         )
