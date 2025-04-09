from typing import Dict, Optional, Any, List
from datetime import datetime
import logging

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.blacklist.models import Blacklist
from apps.blacklist.serializers import BlacklistResponseSerializer

logger = logging.getLogger(__name__)

class BlacklistService:
    """
    Service class for handling blacklist operations.
    
    Follows the Service Layer pattern, encapsulating all business logic
    related to blacklisting users.
    """
    
    @staticmethod
    def check_blacklist_status(npm: str) -> Dict[str, Any]:
        """
        Check if a student is blacklisted based on their NPM.
        
        Args:
            npm: Student's NPM number
            
        Returns:
            Dictionary with blacklist status and information
        """
        logger.info(f"Checking blacklist status for NPM: {npm}")
        
        if not npm:
            logger.warning("Blacklist check attempted with empty NPM")
            return {
                "npm": None,
                "is_blacklisted": False,
                "blacklist_info": None,
                "message": "No NPM provided for blacklist check"
            }
            
        blacklist = Blacklist.get_active_blacklist(npm)
        response_data = BlacklistResponseSerializer.format_response(npm, blacklist)
        
        logger.info(f"Blacklist check result for NPM {npm}: {'Blacklisted' if response_data['is_blacklisted'] else 'Not blacklisted'}")
        return response_data
    
    @staticmethod
    def add_to_blacklist(npm: str, reason: str, end_date: datetime) -> Dict[str, Any]:
        """
        Add a student to the blacklist.
        
        Args:
            npm: Student's NPM number
            reason: Reason for blacklisting
            end_date: End date of blacklist period
            
        Returns:
            Dictionary with operation result
            
        Raises:
            ValidationError: If data validation fails
        """
        logger.info(f"Adding NPM {npm} to blacklist until {end_date}")
        
        if not all([npm, reason, end_date]):
            logger.warning(f"Attempted to add blacklist with missing data: npm={npm}, reason={'Present' if reason else 'Missing'}, end_date={'Present' if end_date else 'Missing'}")
            raise ValidationError("Missing required fields. NPM, reason, and end date are required.")
        
        try:
            # Create a new blacklist entry
            blacklist = Blacklist(
                npm=npm,
                keterangan=reason,
                startDate=timezone.now().date(),
                endDate=end_date
            )
            
            # Validate and save
            blacklist.full_clean()
            blacklist.save()
            
            logger.info(f"Successfully added NPM {npm} to blacklist")
            return {
                "success": True,
                "message": f"Student with NPM {npm} added to blacklist successfully.",
                "blacklist_id": blacklist.id
            }
            
        except ValidationError as e:
            logger.warning(f"Validation error adding NPM {npm} to blacklist: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Error adding NPM {npm} to blacklist: {str(e)}", exc_info=True)
            raise ValidationError(f"Failed to add student to blacklist: {str(e)}")
    
    @staticmethod
    def remove_from_blacklist(npm: str) -> Dict[str, Any]:
        """
        Remove a student from the blacklist.
        
        Args:
            npm: Student's NPM number
            
        Returns:
            Dictionary with operation result
            
        Raises:
            ValidationError: If validation fails or student not found
        """
        logger.info(f"Removing NPM {npm} from blacklist")
        
        if not npm:
            logger.warning("Attempted to remove blacklist with missing NPM")
            raise ValidationError("Missing NPM field.")
        
        try:
            # Find active blacklist entries for this NPM
            blacklist = Blacklist.objects.filter(
                npm=npm, 
                endDate__gte=timezone.now().date()
            )
            
            if not blacklist.exists():
                logger.warning(f"No active blacklist found for NPM {npm}")
                return {
                    "success": False,
                    "message": f"No active blacklist found for student with NPM {npm}."
                }
                
            count = blacklist.delete()[0]
            logger.info(f"Removed {count} blacklist entries for NPM {npm}")
            
            return {
                "success": True,
                "message": f"Removed {count} blacklist entries for student with NPM {npm}."
            }
            
        except Exception as e:
            logger.error(f"Error removing NPM {npm} from blacklist: {str(e)}", exc_info=True)
            raise ValidationError(f"Failed to remove student from blacklist: {str(e)}")
    
    @staticmethod
    def get_all_active_blacklists() -> List[Dict[str, Any]]:
        """
        Get all currently active blacklists.
        
        Returns:
            List of dictionaries with blacklist information
        """
        logger.info("Retrieving all active blacklists")
        
        today = timezone.now().date()
        active_blacklists = Blacklist.objects.filter(
            startDate__lte=today,
            endDate__gte=today
        ).order_by('npm')
        
        result = []
        for blacklist in active_blacklists:
            result.append({
                'id': blacklist.id,
                'npm': blacklist.npm,
                'reason': blacklist.keterangan,
                'start_date': blacklist.startDate,
                'end_date': blacklist.endDate,
                'days_remaining': blacklist.days_remaining
            })
            
        logger.info(f"Retrieved {len(result)} active blacklists")
        return result
    
    @staticmethod
    def get_blacklist_history(npm: str) -> List[Dict[str, Any]]:
        """
        Get blacklist history for a specific student.
        
        Args:
            npm: Student's NPM number
            
        Returns:
            List of dictionaries with blacklist history
        """
        logger.info(f"Retrieving blacklist history for NPM {npm}")
        
        if not npm:
            logger.warning("Attempted to get blacklist history with missing NPM")
            return []
            
        blacklists = Blacklist.objects.filter(npm=npm).order_by('-startDate')
        
        result = []
        for blacklist in blacklists:
            result.append({
                'id': blacklist.id,
                'npm': blacklist.npm,
                'reason': blacklist.keterangan,
                'start_date': blacklist.startDate,
                'end_date': blacklist.endDate,
                'is_active': blacklist.is_active,
                'days_remaining': blacklist.days_remaining
            })
            
        logger.info(f"Retrieved {len(result)} blacklist records for NPM {npm}")
        return result