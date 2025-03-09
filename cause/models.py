from django.db import models
from django.core.exceptions import ValidationError
import uuid
from question.models import Problem

class Causes(models.Model):
    STATUS_CHOICES = [
        ('PRIBADI', 'Pribadi'),
        ('PENGAWASAN', 'Pengawasan'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    problem = models.ForeignKey(Problem, on_delete=models.SET_NULL, null=True, blank=True)  # Untuk guest (blank=True)
    row = models.IntegerField()
    column = models.IntegerField()
    mode = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PRIBADI'
    )
    cause = models.CharField(max_length=120, null=False, default='N/A')
    status = models.BooleanField(default=False)
    root_status = models.BooleanField(default=False)
    feedback = models.CharField(max_length=50, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'validator'

    def __str__(self):
        return f"Cause: {self.cause} ({self.mode})"

    def clean(self):
        if self.problem is None:
            raise ValidationError("Problem reference is required.")
        if not self.cause:
            raise ValidationError("Cause description is required.")
        if self.row < 0 or self.column < 0:
            raise ValidationError("Row and Column values must be non-negative.")
        if self.feedback and len(self.feedback) > 50:
            raise ValidationError("Feedback cannot exceed 50 characters.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
