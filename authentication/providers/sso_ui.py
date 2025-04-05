from typing import Dict, Any, Tuple
import logging

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed

from authentication.providers.base import AuthenticationProvider
from sso_ui.config import SSOJWTConfig
from sso_ui.ticket import validate_ticket, ValidateTicketError
from apps.blacklist.models import Blacklist

User = get_user_model()
logger = logging.getLogger(__name__)

class SSOUIAuthProvider(AuthenticationProvider):
    """
    Authentication provider for SSO UI.
    Handles verification of SSO UI tickets and user creation/retrieval.
    """
    
    def __init__(self):
        self.config = SSOJWTConfig()
    
    def authenticate(self, credential: str) -> Tuple[User, bool]:
        """
        Authenticate a user with an SSO UI ticket.
        
        Args:
            credential: SSO UI ticket
            
        Returns:
            Tuple with the authenticated user and whether they're new
            
        Raises:
            AuthenticationFailed: If authentication fails
            AuthenticationFailed with blacklist info: If user is blacklisted
        """
        user_info = self.validate_credential(credential)
        
        # Check for blacklist before proceeding
        npm = user_info.get('attributes', {}).get('npm')
        if npm:
            blacklist_entry = Blacklist.get_active_blacklist(npm)
            if blacklist_entry:
                raise AuthenticationFailed({
                    "error": "User is blacklisted",
                    "blacklist_info": {
                        "npm": npm,
                        "reason": blacklist_entry.keterangan,
                        "blacklisted_at": blacklist_entry.startDate.isoformat(),
                        "expires_at": blacklist_entry.endDate.isoformat() if blacklist_entry.endDate else None
                    }
                })
        
        return self.get_or_create_user(user_info)
    
    def validate_credential(self, credential: str) -> Dict[str, Any]:
        """
        Validate SSO UI ticket and return user information.
        
        Args:
            credential: SSO UI ticket
            
        Returns:
            Dict containing user information from SSO UI
            
        Raises:
            AuthenticationFailed: If ticket validation fails
        """
        if not credential:
            raise AuthenticationFailed("SSO UI ticket is required")
            
        try:
            # Validate ticket with SSO UI
            service_response = validate_ticket(self.config, credential)
            
            auth_success = service_response.get("authentication_success")
            if not auth_success:
                raise AuthenticationFailed("Invalid SSO response")
                
            username = auth_success.get("user")
            if not username:
                raise AuthenticationFailed("Username not provided by SSO")
                
            return auth_success
            
        except ValidateTicketError as e:
            logger.error(f"SSO ticket validation error: {str(e)}")
            raise AuthenticationFailed(f"SSO ticket validation failed: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error during SSO ticket validation")
            raise AuthenticationFailed(f"Ticket verification failed: {str(e)}")
    
    def get_or_create_user(self, user_info: Dict[str, Any]) -> Tuple[User, bool]:
        """
        Get or create a user based on SSO UI information.
        
        Args:
            user_info: User information from SSO UI
            
        Returns:
            Tuple containing the user and whether they were created
        """
        username = user_info.get("user")
        attributes = user_info.get("attributes", {})
        
        npm = attributes.get("npm")
        nama = attributes.get("nama", "")
        
        # Parse name into first/last name
        if nama and " " in nama:
            first_name, last_name = nama.split(" ", 1)
        else:
            first_name, last_name = nama, ""
            
        email = f"{username}@ui.ac.id"
        
        # Try to find user by NPM or username
        user = None
        created = False
        
        if npm:
            user = User.objects.filter(npm=npm).first()
            
        if not user:
            user = User.objects.filter(username=username).first()
            
        if not user:
            user = User.objects.filter(email=email).first()
            
        if user:
            self._update_user_info(user, username, email, npm, first_name, last_name)    # Update existing user
        else:
            user = self._create_new_user(username, email, npm, first_name, last_name)    # Create new user
            created = True
            
        return user, created
        
    def _create_new_user(self, username, email, npm, first_name, last_name) -> User:
        """
        Create a new user from SSO UI information.
        
        Args:
            username: SSO UI username
            email: User's UI email
            npm: Student ID number
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            The newly created user
        """

        # Determine angkatan (student year) from NPM
        angkatan = npm[:2] if npm and len(npm) >= 2 else None
        
        user = User.objects.create_user(
            username=username,
            email=email,
            npm=npm,
            first_name=first_name,
            last_name=last_name,
            angkatan=angkatan,
            role='user'
        )
        
        logger.info(f"Created new user via SSO UI: {username}")
        return user
        
    def _update_user_info(self, user, username, email, npm, first_name, last_name) -> None:
        """
        Update existing user with SSO UI information.
        
        Args:
            user: The user to update
            username: SSO UI username
            email: User's UI email
            npm: Student ID number
            first_name: User's first name
            last_name: User's last name
        """
        update_fields = []
        
        # Only update email if it follows the UI format and user's email is empty
        if not user.email and email.endswith('@ui.ac.id'):
            user.email = email
            update_fields.append('email')
            
        # Update NPM if not set
        if npm and not user.npm:
            user.npm = npm
            update_fields.append('npm')
            
            # Update angkatan if NPM is being set
            angkatan = npm[:2] if len(npm) >= 2 else None
            if angkatan and not user.angkatan:
                user.angkatan = angkatan
                update_fields.append('angkatan')
            
        # Update names if they're empty
        if not user.first_name and first_name:
            user.first_name = first_name
            update_fields.append('first_name')
            
        if not user.last_name and last_name:
            user.last_name = last_name
            update_fields.append('last_name')
            
        if update_fields:
            user.save(update_fields=update_fields)
            logger.info(f"Updated user info for {user.username}: {', '.join(update_fields)}")