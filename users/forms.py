from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import Form
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser


class SomethingFrom(Form):
    pass
