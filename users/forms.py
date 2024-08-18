from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')  # Agrega otros campos si es necesario

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
