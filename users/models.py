from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Agrega campos personalizados aquí si es necesario
    pass