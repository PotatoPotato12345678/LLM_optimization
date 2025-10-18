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
    availability_calendar = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.employee.username}: {self.year}-{self.month}"
class ManagerRequirement(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    hard_rule = models.JSONField(default=dict)  # Changed to JSONField
    content = models.TextField(blank=True, null=True)  # Optional notes
    created_at = models.DateTimeField(auto_now_add=True)  # ← ensures automatic timestamp
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        unique_together = ("manager", "year", "month")