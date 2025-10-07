from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model() 

class ShiftRequirement(models.Model):
    """
    Attributes:
        content    : shift requirement text
        author     : ForeignKey to User model
    """
    content = models.CharField(max_length=150, unique=False)
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField(null=False, default=2025)
    month = models.PositiveSmallIntegerField(null=False, default=11)
    def __str__(self):
        return f"{self.employee.username}: {self.year}-{self.month}"