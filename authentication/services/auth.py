from typing import Dict, Tuple, Any
import logging

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed

from authentication.providers.factory import AuthProviderFactory
from authentication.services.interfaces import TokenServiceInterface

User = get_user_model()

class AuthenticationService:
    """
    Authentication service for handling user authentication from different providers.
    
    This service follows the Facade pattern by providing a simplified interface
    to the complex authentication subsystem and the Repository pattern by
    abstracting the authentication logic.
    """
    
    def __init__(self, token_service: TokenServiceInterface):
        self.token_service = token_service
    
    def authenticate_with_provider(self, provider_type: str, credential: str) -> tuple:
        """
        Authenticate a user using the specified provider.
        
        Args:
            provider_type: The type of authentication provider to use
            credential: The authentication credential (e.g., ticket, token)
            
        Returns:
            tuple: (tokens, user, is_new_user)
            
        Raises:
            AuthenticationFailed: If authentication fails
        """
        try:
            # Get the appropriate provider
            provider = AuthProviderFactory.get_provider(provider_type)
            
            # Authenticate the user
            user, is_new_user = provider.authenticate(credential)
            
            # Generate tokens
            tokens = self.token_service.generate_tokens(user)
            
            return tokens, user, is_new_user
        except AuthenticationFailed:
            # Re-raise AuthenticationFailed exceptions
            raise
        except Exception as e:
            # Convert other exceptions to AuthenticationFailed
            raise AuthenticationFailed(f"Authentication failed: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token to use
            
        Returns:
            dict: New access token
            
        Raises:
            AuthenticationFailed: If token refresh fails
        """
        try:
            # Validate the refresh token
            payload = self.token_service.validate_refresh_token(refresh_token)
            
            # Create a new access token
            access_token = self.token_service.create_access_token(payload)
            
            return {'access': access_token}
            
        except Exception as e:
            raise AuthenticationFailed(f"Token refresh failed: {str(e)}")
    
    def logout(self, refresh_token: str) -> bool:
        """
        Logout a user by invalidating their refresh token.
        
        Args:
            refresh_token: The refresh token to invalidate
            
        Returns:
            bool: True if logout was successful
        """
        try:
            # Validate the refresh token
            self.token_service.validate_refresh_token(refresh_token)
            return True
        except Exception:
            return False
    
    def validate_token(self, token: str, token_type: str = 'access') -> Dict[str, Any]:
        """
        Validate a token and return its payload.
        
        Args:
            token: The token to validate
            token_type: The type of token ('access' or 'refresh')
            
        Returns:
            Dictionary containing the token payload
            
        Raises:
            Exception: If token validation fails
        """
        return self.token_service.validate_token(token, token_type)