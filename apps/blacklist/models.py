from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

class Blacklist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    npm = models.CharField(max_length=10)
    startDate = models.DateField()
    endDate = models.DateField()
    keterangan = models.TextField()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['npm'],
                condition=models.Q(endDate__gte=timezone.now().date()),
                name='unique_active_blacklist'
            )
        ]
        indexes = [
            models.Index(fields=['npm', 'startDate', 'endDate'], name='blacklist_search_idx'),
        ]

    def __str__(self):
        return f"Blacklist-{self.npm} ({self.startDate} - {self.endDate}), {self.keterangan}"
    
    def clean(self):
        if self.startDate is not None and self.endDate is not None:
            if self.endDate < self.startDate:
                raise ValidationError("End date cannot be before start date")
        
        if self.startDate is None:
            raise ValidationError("Start date is required")
        if self.endDate is None:
            raise ValidationError("End date is required")
        if not self.npm:
            raise ValidationError("NPM is required")
        if not self.keterangan:
            raise ValidationError("Keterangan is required")
         
        overlapping = Blacklist.objects.filter(
            npm=self.npm,
            startDate__lte=self.endDate,
            endDate__gte=self.startDate
        )
        
        if self.pk and not self._state.adding:
            overlapping = overlapping.exclude(pk=self.pk)
            
        if overlapping.exists():
            raise ValidationError(
                f"This student already has a blacklist record for an overlapping period. "
                f"Existing record: {overlapping.first()}"
            )
    
    def save(self, *args, **kwargs):
        try:
            self.full_clean()
            result = super().save(*args, **kwargs)
            return result
        except ValidationError as e:
            raise ValidationError("Validation error occurred: " + str(e))
    
    def delete(self, *args, **kwargs):
        try:
            result = super().delete(*args, **kwargs)
            return result
        except Exception as e:
            raise
    
    @property
    def is_active(self):
        today = timezone.now().date()
        result = self.startDate <= today <= self.endDate
        return self.startDate <= today <= self.endDate
    
    @property
    def days_remaining(self):
        today = timezone.now().date()
        if today > self.endDate:
            return 0
        if today < self.startDate:
            days = (self.endDate - self.startDate).days
            return days
        days = (self.endDate - today).days
        return days
    
    @classmethod
    def is_user_blacklisted(cls, npm):
        today = timezone.now().date()
        result = cls.objects.filter(
            npm=npm,
            startDate__lte=today,
            endDate__gte=today
        ).exists()
        return result
    
    @classmethod
    def get_active_blacklist(cls, npm):
        today = timezone.now().date()
        blacklist = cls.objects.filter(
            npm=npm,
            startDate__lte=today,
            endDate__gte=today
        ).first()
        
        return blacklist