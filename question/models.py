from django.db import models
import uuid
from tag.models import Tag

class Question(models.Model):
    class Meta:
        app_label = 'validator'
        
    class ModeChoices(models.TextChoices):
        PRIBADI = "PRIBADI", "pribadi"
        PENGAWASAN = "PENGAWASAN", "pengawasan"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=40, default='')
    question = models.CharField(max_length=255)
    mode = models.CharField(max_length=20, choices=ModeChoices.choices, default=ModeChoices.PRIBADI)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
