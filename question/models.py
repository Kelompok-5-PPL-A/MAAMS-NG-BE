from django.db import models
import uuid
from authentication.models import CustomUser
from tag.models import Tag
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Question(models.Model):
    class Meta:
        app_label = 'question'
        db_table = 'question_question'
        
    class ModeChoices(models.TextChoices):
        PRIBADI = "PRIBADI", "pribadi"
        PENGAWASAN = "PENGAWASAN", "pengawasan"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=40, default='')
    question = models.CharField(max_length=255)
    mode = models.CharField(max_length=20, choices=ModeChoices.choices, default=ModeChoices.PRIBADI)
    created_at = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='question',
    )

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now() + timedelta(hours=7)
        super().save(*args, **kwargs)