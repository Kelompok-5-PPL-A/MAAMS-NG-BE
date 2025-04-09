from django.db import models
import uuid
from authentication.models import CustomUser
from tag.models import Tag
from django.conf import settings

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
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='question',
    )