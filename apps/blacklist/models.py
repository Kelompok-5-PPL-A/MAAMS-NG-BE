from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
import logging

logger = logging.getLogger(__name__)

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
         
        logger.debug(f"Checking for overlapping blacklists for NPM: {self.npm}")
        overlapping = Blacklist.objects.filter(
            npm=self.npm,
            startDate__lte=self.endDate,
            endDate__gte=self.startDate
        )
        
        if self.pk and not self._state.adding:
            overlapping = overlapping.exclude(pk=self.pk)
            
        if overlapping.exists():
            overlap = overlapping.first()
            logger.warning(f"Overlapping blacklist found for NPM {self.npm}: existing entry from {overlap.startDate} to {overlap.endDate}")
            raise ValidationError(
                f"This student already has a blacklist record for an overlapping period. "
                f"Existing record: {overlapping.first()}"
            )
        
        logger.debug(f"Blacklist validation successful for NPM: {self.npm}")
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        action = "Creating" if is_new else "Updating"
        logger.info(f"{action} blacklist entry for NPM: {self.npm}, period: {self.startDate} to {self.endDate}")
        
        try:
            self.full_clean()
            result = super().save(*args, **kwargs)
            logger.info(f"Successfully {action.lower()}d blacklist entry for NPM: {self.npm}")
            return result
        except ValidationError as e:
            logger.error(f"Failed to {action.lower()} blacklist entry for NPM: {self.npm} - {str(e)}")
            raise
    
    def delete(self, *args, **kwargs):
        logger.info(f"Deleting blacklist entry for NPM: {self.npm}, period: {self.startDate} to {self.endDate}")
        try:
            result = super().delete(*args, **kwargs)
            logger.info(f"Successfully deleted blacklist entry for NPM: {self.npm}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete blacklist entry for NPM: {self.npm} - {str(e)}")
            raise
    
    @property
    def is_active(self):
        today = timezone.now().date()
        result = self.startDate <= today <= self.endDate
        logger.debug(f"Blacklist status check for NPM {self.npm}: {'Active' if result else 'Inactive'}")
        return self.startDate <= today <= self.endDate
    
    @property
    def days_remaining(self):
        today = timezone.now().date()
        if today > self.endDate:
            logger.debug(f"Blacklist for NPM {self.npm} has expired (0 days remaining)")
            return 0
        if today < self.startDate:
            days = (self.endDate - self.startDate).days
            logger.debug(f"Blacklist for NPM {self.npm} has not started yet ({days} days total duration)")
            return days
        days = (self.endDate - today).days
        logger.debug(f"Blacklist for NPM {self.npm} has {days} days remaining")
        return days
    
    @classmethod
    def is_user_blacklisted(cls, npm):
        logger.debug(f"Checking if NPM {npm} is blacklisted")
        today = timezone.now().date()
        result = cls.objects.filter(
            npm=npm,
            startDate__lte=today,
            endDate__gte=today
        ).exists()
        logger.info(f"Blacklist check for NPM {npm}: {'Blacklisted' if result else 'Not blacklisted'}")
        return result
    
    @classmethod
    def get_active_blacklist(cls, npm):
        logger.debug(f"Retrieving active blacklist for NPM {npm}")
        today = timezone.now().date()
        blacklist = cls.objects.filter(
            npm=npm,
            startDate__lte=today,
            endDate__gte=today
        ).first()
        
        if blacklist:
            logger.info(f"Active blacklist found for NPM {npm}, ending on {blacklist.endDate}")
        else:
            logger.info(f"No active blacklist found for NPM {npm}")
        return blacklist