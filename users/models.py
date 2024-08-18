# users/models.py
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # edit as necessary
    # bio = models.TextField(blank=True, null=True)
    pass
