from django.db import models
class OptimizedShift(models.Model):
    """
    Attributes:
        shift    : optimized shift schedule (JSON)
    """
    shift = models.JSONField(default=dict)
    year = models.IntegerField(null=False, default=2025)
    month = models.PositiveSmallIntegerField(null=False, default=11)
    publish_status = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.year}-{self.month}, publish_status: {self.publish_status}"