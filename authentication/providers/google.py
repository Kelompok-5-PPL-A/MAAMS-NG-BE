from typing import Dict, Any, Tuple
import logging

from django.contrib.auth import get_user_model
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.exceptions import AuthenticationFailed, ParseError

from authentication.providers.base import AuthenticationProvider

User = get_user_model()
logger = logging.getLogger(__name__)

class GoogleAuthProvider(AuthenticationProvider):
    """
    Authentication provider for Google OAuth.
    Handles verification of Google ID tokens and user creation/retrieval.
    """
    
    def authenticate(self, credential: str) -> Tuple[User, bool]:
        """
        Authenticate a user with a Google ID token.
        
        Args:
            credential: Google ID token
            
        Returns:
            Tuple with the authenticated user and whether they're new
            
        Raises:
            AuthenticationFailed: If authentication fails
        """
        user_info = self.validate_credential(credential)
        return self.get_or_create_user(user_info)
    
    def validate_credential(self, credential: str) -> Dict[str, Any]:
        """
        Validate Google ID token and return user information.
        
        Args:
            credential: Google ID token
            
        Returns:
            Dict containing user information from the Google token
            
        Raises:
            AuthenticationFailed: If token validation fails
        """
        if not credential:
            raise ParseError("Google ID token is required")
            
        try:
            # Verify the ID token with Google
            client_id = settings.GOOGLE_CLIENT_ID

            user_info = id_token.verify_oauth2_token(
                credential, 
                google_requests.Request(),
                audience=client_id
            )
            
            # Validate token data
            if not user_info or 'sub' not in user_info:
                raise AuthenticationFailed("Invalid Google token data")
                
            if not user_info.get('email'):
                raise AuthenticationFailed("Email not provided by Google")
                
            return user_info
            
        except ValueError as e:
            logger.error(f"Google token validation error: {str(e)}")
            raise AuthenticationFailed(f"Invalid Google token: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error during Google token validation")
            raise AuthenticationFailed(f"Token verification failed: {str(e)}")
    
    def get_or_create_user(self, user_info: Dict[str, Any]) -> Tuple[User, bool]:
        """
        Get or create a user based on Google account information.
        
        Args:
            user_info: User information from Google
            
        Returns:
            Tuple containing the user and whether they were created
        """
        google_id = user_info['sub']
        email = user_info['email']
        
        # First try to find by Google ID
        try:
            user = User.objects.get(google_id=google_id)
            # User exists, update their information if needed
            self._update_user_if_needed(user, user_info)
            return user, False
        except User.DoesNotExist:
            pass
            
        # Then try by email
        try:
            user = User.objects.get(email=email)

            # User exists but wasn't linked to this Google account
            if not user.google_id:
                user.google_id = google_id
                user.save(update_fields=['google_id'])
            return user, False
        except User.DoesNotExist:
            pass
            
        # Create a new user
        return self._create_new_user(user_info), True
        
    def _create_new_user(self, user_info: Dict[str, Any]) -> User:
        """
        Create a new user from Google account information.
        
        Args:
            user_info: User information from Google
            
        Returns:
            The newly created user
        """
        google_id = user_info['sub']
        email = user_info['email']
        
        user = User.objects.create_user(
            email=email,
            username=email,
            google_id=google_id,
            first_name=user_info.get('given_name'),
            last_name=user_info.get('family_name'),
            role='user'
        )
        
        logger.info(f"Created new user via Google OAuth: {email}")
        return user
    
    def _update_user_if_needed(self, user: User, user_info: Dict[str, Any]) -> None:
        """
        Update user information if needed.
        
        Args:
            user: The user to update
            user_info: New user information from Google
        """
        update_fields = []
        
        if not user.first_name and user_info.get('given_name'):
            user.first_name = user_info['given_name']
            update_fields.append('first_name')
            
        if not user.last_name and user_info.get('family_name'):
            user.last_name = user_info['family_name']
            update_fields.append('last_name')
            
        if update_fields:
            user.save(update_fields=update_fields)
            logger.info(f"Updated user info for {user.email}: {', '.join(update_fields)}")