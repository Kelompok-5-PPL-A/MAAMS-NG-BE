from django.db import models
from django.core.exceptions import ValidationError
import uuid

class Problem(models.Model):
    STATUS_CHOICES = [
        ('PRIBADI', 'Pribadi'),
        ('PENGAWASAN', 'Pengawasan'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_email = models.EmailField(null=True)
    title = models.CharField(max_length=255, null=False, default='N/A')
    question = models.CharField(max_length=255, null=False, default='N/A')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PRIBADI'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
    
    def clean(self):
        if not self.title:
            raise ValidationError('Title is required.')
        if not self.question:
            raise ValidationError('Question content is required.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)