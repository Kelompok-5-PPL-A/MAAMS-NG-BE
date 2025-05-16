from typing import Dict, Any, Tuple
import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed

from authentication.providers.base import AuthenticationProvider
from sso_ui.config import SSOJWTConfig
from sso_ui.ticket import validate_ticket, ValidateTicketError

User = get_user_model()

class SSOUIAuthProvider(AuthenticationProvider):
    """
    Authentication provider for SSO UI CAS.
    
    Handles authentication through the SSO UI CAS service.
    """
    
    def __init__(self):
        self.config = SSOJWTConfig()
        
    def validate_credential(self, credential: str) -> dict:
        """
        Validate an SSO UI CAS ticket.
        
        Args:
            credential: The SSO UI CAS ticket to validate
            
        Returns:
            dict: User information from the ticket
            
        Raises:
            AuthenticationFailed: If ticket validation fails
        """
        if not credential:
            raise AuthenticationFailed("Missing ticket")
            
        try:
            # Validate the ticket with SSO UI
            response = validate_ticket(self.config, credential)
            
            # Extract user info
            user_info = response.get("authentication_success")
            if not user_info:
                raise AuthenticationFailed("Invalid ticket response")
                
            return user_info
            
        except ValidateTicketError as e:
            raise AuthenticationFailed(str(e))
        except Exception as e:
            raise AuthenticationFailed(f"Unexpected error: {str(e)}")
            
    def authenticate(self, credential: str) -> tuple:
        """
        Authenticate a user with an SSO UI CAS ticket.
        
        Args:
            credential: The SSO UI CAS ticket
            
        Returns:
            tuple: (User, bool) - The authenticated user and whether they are new
            
        Raises:
            AuthenticationFailed: If authentication fails
        """
        # Validate the ticket
        user_info = self.validate_credential(credential)
        
        # Get or create the user
        user, is_new = self.get_or_create_user(user_info)
        
        return user, is_new
        
    def get_or_create_user(self, user_info: dict) -> tuple:
        """
        Get an existing user or create a new one based on SSO UI info.
        
        Args:
            user_info: User information from SSO UI
            
        Returns:
            tuple: (User, bool) - The user and whether they are new
        """
        username = user_info.get("user")
        attributes = user_info.get("attributes", {})
        npm = attributes.get("npm")
        nama = attributes.get("nama", "")
        
        if not username or not npm:
            raise AuthenticationFailed("Missing required user information")
            
        # Try to find existing user by NPM
        user = User.objects.filter(npm=npm).first()
        
        if not user:
            # Try to find by username
            user = User.objects.filter(username=username).first()
            
        if not user:
            # Try to find by email
            email = f"{username}@ui.ac.id"
            user = User.objects.filter(email=email).first()
            
        if not user:
            # Create new user
            first_name, *last_name_parts = nama.split()
            last_name = " ".join(last_name_parts) if last_name_parts else ""
            
            user = User.objects.create_user(
                username=username,
                email=f"{username}@ui.ac.id",
                npm=npm,
                first_name=first_name,
                last_name=last_name,
                date_joined=timezone.now()
            )
            return user, True
            
        # Update user info
        self._update_user_info(user, username, f"{username}@ui.ac.id", npm, nama)
        return user, False
        
    def _update_user_info(self, user: User, username: str, email: str, npm: str, nama: str) -> None:
        """
        Update user information from SSO UI.
        
        Args:
            user: The user to update
            username: SSO UI username
            email: User's email
            npm: Student ID number
            nama: Full name
        """
        # Only update email if it's from UI domain
        if email.endswith("@ui.ac.id"):
            user.email = email
            
        # Update other fields
        user.username = username
        user.npm = npm
        
        # Update name if provided
        if nama:
            first_name, *last_name_parts = nama.split()
            last_name = " ".join(last_name_parts) if last_name_parts else ""
            user.first_name = first_name
            user.last_name = last_name
            
        user.save()