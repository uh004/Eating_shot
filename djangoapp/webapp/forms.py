from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import (
    CustomUser,
    Diet,
    Exercise,
    BloodSugar,
    BloodPressure,
    HbA1c,
    PillAlarm,
    HospitalAlarm,
)


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]
        error_messages = {
            "username": {
                "unique": "이미 존재하는 사용자 이름입니다.",
            },
            "email": {
                "unique": "이미 존재하는 이메일입니다.",
            },
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                "비밀번호가 일치하지 않습니다.",
                code="password_mismatch",
            )
        try:
            validate_password(password2, self.instance)
        except ValidationError as error:
            self.add_error("password2", error)
        return password2

    def add_error(self, field, error):
        if isinstance(error, ValidationError):
            if field == "password2":
                new_error_list = []
                for e in error.error_list:
                    if e.code == "password_too_short":
                        e.message = "비밀번호는 8자 이상이어야 합니다."
                    elif e.code == "password_too_common":
                        e.message = "너무 일반적인 비밀번호입니다."
                    elif e.code == "password_entirely_numeric":
                        e.message = "비밀번호는 숫자로만 이루어질 수 없습니다."
                    elif e.code == "password_too_similar":
                        e.message = "비밀번호가 사용자 이름과 유사합니다."
                    new_error_list.append(e)
                error.error_list = new_error_list
        super().add_error(field, error)

    def is_valid(self) -> bool:
        is_valid = super().is_valid()
        if not is_valid:
            for field, errors in self.errors.items():
                if field in self.fields:
                    self.fields[field].widget.attrs["class"] = "general-error"
                    self.fields[field].widget.attrs["placeholder"] = errors[0]
                    self.data = self.data.copy()
                    self.data[field] = ""
        return is_valid


class CustomAuthenticationForm(AuthenticationForm):

    class Meta:
        model = CustomUser
        fields = ["username", "password"]
        error_messages = {
            "username": {
                "required": "사용자 이름을 입력해주세요.",
                "invalid": "유효한 사용자 이름을 입력해주세요.",
            },
            "password": {
                "required": "비밀번호를 입력해주세요.",
                "invalid_login": "사용자 이름 또는 비밀번호가 올바르지 않습니다.",
            },
        }

    def is_valid(self) -> bool:
        for item in self.errors.as_data().items():
            if item[0] in self.fields:
                print(item[0])
                self.fields[item[0]].widget.attrs["class"] = "general-error"
                self.fields[item[0]].widget.attrs["placeholder"] = item[1][0].message

        return super().is_valid()


class HealthInfoForm(forms.Form):
    height = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(0), MaxValueValidator(300)],
    )
    weight = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(0)],
    )
    # age = forms.IntegerField(required=True)
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
        required=True,
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


# class InstantDietForm(forms.Form):
#     food_name = forms.CharField(
#         widget=forms.TextInput(attrs={"placeholder": "음식 이름"}),
#         label="음식 이름",
#         required=True,
#     )
#
#     class Meta:
#         model = InferenceResult
#         fields = ["result_names_comma_separated", "modified_at"]


class ExerciseForm(forms.ModelForm):
    EXERCISE_INTENSITY_CHOICES = [
        ("가볍게", "가볍게"),
        ("적당히", "적당히"),
        ("격하게", "격하게"),
    ]

    exercise_time = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "시간(분)"}),
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
        validators=[MinValueValidator(0)],
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
        validators=[MinValueValidator(0)],
        required=True,
    )
    diastolic = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "80"}),
        label="이완기",
        validators=[MinValueValidator(0)],
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
        validators=[MinValueValidator(0)],
        required=True,
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="날짜", required=True
    )

    class Meta:
        model = HbA1c
        fields = ["hba1c", "date"]


class MyPageReviseForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "내가 입력했던 이메일"}),
        label="E-mail",
        required=True,
    )
    height = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "내가 입력했던 키"}),
        label="키(cm)",
        validators=[MinValueValidator(0), MaxValueValidator(300)],
        required=True,
    )
    weight = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "내가 입력했던 몸무게"}),
        label="몸무게(kg)",
        validators=[MinValueValidator(0)],
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
        widget=forms.CheckboxSelectMultiple,
        label="질병",
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = ["email", "height", "weight", "health_conditions"]

    def save(self, commit=True):
        health_conditions = self.cleaned_data["health_conditions"]
        health_conditions = ",".join(health_conditions)
        self.instance.health_conditions = health_conditions
        return super().save(commit)


class PillAlarmForm(forms.ModelForm):
    pill_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "약 이름"}),
        label="약 이름",
        required=True,
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}), label="시간", required=True
    )
    weekday = forms.MultipleChoiceField(
        choices=[
            ("mon", "월"),
            ("tue", "화"),
            ("wed", "수"),
            ("thu", "목"),
            ("fri", "금"),
            ("sat", "토"),
            ("sun", "일"),
        ],
        widget=forms.CheckboxSelectMultiple,
        label="요일",
        required=True,
    )

    class Meta:
        model = PillAlarm
        fields = ["pill_name", "time", "weekday"]

    def save(self, commit=True):
        weekday = self.cleaned_data["weekday"]
        weekday = ",".join(weekday)
        self.instance.weekday = weekday
        return super().save(commit)


class HospitalAlarmForm(forms.ModelForm):
    hospital_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "병원 이름"}),
        label="병원 이름",
        required=True,
    )
    hospital_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="날짜", required=True
    )
    hospital_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}), label="시간", required=True
    )

    class Meta:
        model = HospitalAlarm
        fields = ["hospital_name", "hospital_date", "hospital_time"]
