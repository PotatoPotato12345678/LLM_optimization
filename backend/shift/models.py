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
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name="manager_shift_requirements")
    year = models.IntegerField()
    month = models.IntegerField()
    hard_rule = models.TextField(default="", blank=True)
    content = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('year', 'month')  # one per month
        ordering = ['-year', '-month']

    def __str__(self):
        return f"ManagerShiftRequirement({self.year}-{self.month})"