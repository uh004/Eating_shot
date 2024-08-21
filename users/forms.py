from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser


class HealthInfoForm(forms.Form):
    height = forms.IntegerField(required=True)
    weight = forms.IntegerField(required=True)
    age = forms.IntegerField(required=True)
    birthdate = forms.DateField(required=True)
    gender = forms.ChoiceField(
        choices=[("male", "Male"), ("female", "Female")], required=True
    )
    goal = forms.ChoiceField(
        choices=[
            ("chronic_disease", "만성질환"),
            ("healthy_diet", "건강한 식습관, 체중 감량"),
        ],
        required=True,
    )
    health_conditions = forms.MultipleChoiceField(
        choices=[
            ("type1", "1형 당뇨"),
            ("type2", "2형 당뇨"),
            ("gestational", "임신성 당뇨"),
            ("prediabetes", "내당증"),
            ("high", "고혈압"),
            ("low", "저혈압"),
            ("hyperlipidemia", "고지혈증"),
            ("obesity", "비만"),
        ],
    )
