from typing import Dict, Optional, Any, List
from datetime import datetime
import logging

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.blacklist.models import Blacklist
from apps.blacklist.serializers import BlacklistResponseSerializer

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
        if not npm:
            return {
                "npm": None,
                "is_blacklisted": False,
                "blacklist_info": None,
                "message": "No NPM provided for blacklist check"
            }
            
        blacklist = Blacklist.get_active_blacklist(npm)
        response_data = BlacklistResponseSerializer.format_response(npm, blacklist)

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
        
        if not all([npm, reason, end_date]):
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
            
            return {
                "success": True,
                "message": f"Student with NPM {npm} added to blacklist successfully.",
                "blacklist_id": blacklist.id
            }
            
        # except ValidationError as e:
        #     raise
            
        except Exception as e:
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
        if not npm:
            raise ValidationError("Missing NPM field.")
        
        try:
            # Find active blacklist entries for this NPM
            blacklist = Blacklist.objects.filter(
                npm=npm, 
                endDate__gte=timezone.now().date()
            )
            
            if not blacklist.exists():
                return {
                    "success": False,
                    "message": f"No active blacklist found for student with NPM {npm}."
                }
                
            count = blacklist.delete()[0]
            
            return {
                "success": True,
                "message": f"Removed {count} blacklist entries for student with NPM {npm}."
            }
            
        except Exception as e:
            raise ValidationError(f"Failed to remove student from blacklist: {str(e)}")
    
    @staticmethod
    def get_all_active_blacklists() -> List[Dict[str, Any]]:
        """
        Get all currently active blacklists.
        
        Returns:
            List of dictionaries with blacklist information
        """

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
        
        if not npm:
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
            
        return result