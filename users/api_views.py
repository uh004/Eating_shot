from rest_framework import viewsets
from .models import CustomUser
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


# TODO: implement api based login and registration (password change , password reset, etc. too)
# TODO: with swagger ui (drf_spectacular)
