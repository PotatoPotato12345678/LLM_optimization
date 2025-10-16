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
    

    # manager = models.ForeignKey(User, on_delete=models.CASCADE)
    # workplace_name = models.CharField(max_length=255)
    # num_shifts_per_day = models.IntegerField(default=2)
    # working_days = models.JSONField(default=list)
    # allow_weekend_work = models.BooleanField(default=False)
    # max_consecutive_shifts = models.IntegerField(default=5)
    # min_rest_hours = models.IntegerField(default=8)
    # publish_auto = models.BooleanField(default=False)