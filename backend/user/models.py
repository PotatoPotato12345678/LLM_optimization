from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Attributes:
        username      : unique username field
        password      : Password field
    
    Note:
        Manager login with their name and password.
        No validation or security measures are implemented for simplicity.
        no cares about the duplicated usernames
    """
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return self.username