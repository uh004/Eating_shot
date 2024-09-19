from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

from users.models import CustomUser, Diet, Exercise, BloodSugar, BloodPressure, HbA1c


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


# diet upload picture
class DietForm(forms.ModelForm):
    MEAL_CHOICES = [
        ("아침", "아침"),
        ("점심", "점심"),
        ("저녁", "저녁"),
        ("간식", "간식"),
    ]

    meal_type = forms.ChoiceField(
        choices=MEAL_CHOICES, label="식사 종류", required=True
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="날짜", required=True
    )
    image = forms.ImageField(label="식단 사진", required=True)

    class Meta:
        model = Diet
        fields = ["meal_type", "date", "image"]


class ExerciseForm(forms.ModelForm):
    EXERCISE_INTENSITY_CHOICES = [
        ("가볍게", "가볍게"),
        ("적당히", "적당히"),
        ("격하게", "격하게"),
    ]

    exercise_time = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "30분"}),
        label="운동 시간",
        required=True,
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="날짜", required=True
    )
    intensity = forms.ChoiceField(
        choices=EXERCISE_INTENSITY_CHOICES,
        widget=forms.RadioSelect,
        label="운동 강도",
        required=True,
    )

    class Meta:
        model = Exercise
        fields = ["exercise_time", "date", "intensity"]


# 혈당
class BloodSugarForm(forms.ModelForm):
    CHOICES = [
        ("아침 식전", "아침 식전"),
        ("점심 식전", "점심 식전"),
        ("저녁 식전", "저녁 식전"),
        ("아침 식후", "아침 식후"),
        ("점심 식후", "점심 식후"),
        ("저녁 식후", "저녁 식후"),
        ("공복", "공복"),
    ]
    time = forms.ChoiceField(choices=CHOICES, label="시간", required=True)
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="날짜", required=True
    )
    blood_sugar = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "100"}),
        label="혈당 수치",
        required=True,
    )

    class Meta:
        model = BloodSugar
        fields = ["time", "date", "blood_sugar"]


# 혈압
class BloodPressureForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="날짜", required=True
    )
    systolic = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "120"}),
        label="수축기",
        required=True,
    )
    diastolic = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "80"}),
        label="이완기",
        required=True,
    )

    class Meta:
        model = BloodPressure
        fields = ["date", "systolic", "diastolic"]


# 당화혈색소
class HbA1cForm(forms.ModelForm):
    hba1c = forms.FloatField(
        widget=forms.NumberInput(attrs={"placeholder": "6.5"}),
        label="당화혈색소",
        required=True,
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="날짜", required=True
    )

    class Meta:
        model = HbA1c
        fields = ["hba1c", "date"]
