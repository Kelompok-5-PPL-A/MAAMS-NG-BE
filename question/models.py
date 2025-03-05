from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import uuid

class Problem(models.Model):
    STATUS_CHOICES = [
        ('PRIBADI', 'Pribadi'),
        ('PENGAWASAN', 'Pengawasan'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_email = models.EmailField()
    title = models.CharField(max_length=255, null=False)
    question = models.CharField(max_length=255, null=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PRIBADI'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
    
    def clean(self):
        if not self.user_email:
            raise ValidationError('User email is required.')
        try:
            validate_email(self.user_email)
        except ValidationError:
            raise ValidationError('Invalid email format.')
        if not self.title:
            raise ValidationError('Title is required.')
        if not self.question:
            raise ValidationError('Question content is required.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)