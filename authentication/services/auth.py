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
    
    def authenticate_with_provider(
        self, 
        provider_type: str, 
        credential: str
    ) -> Tuple[Dict[str, str], User, bool]:
        """
        Authenticate a user with a specific provider.
        
        Args:
            provider_type: The type of authentication provider to use
            credential: The credential to authenticate with
            
        Returns:
            Tuple containing:
                - Dictionary with tokens
                - Authenticated user
                - Boolean indicating if this is a new user
                
        Raises:
            AuthenticationFailed: If authentication fails
        """
        try:
            # Get the appropriate provider
            provider = AuthProviderFactory.get_provider(provider_type)
            
            # Authenticate using the provider
            user, is_new_user = provider.authenticate(credential)
            
            # Generate tokens
            tokens = self.token_service.generate_tokens(user)
            
            return tokens, user, is_new_user
            
        except AuthenticationFailed:
            # Re-raise authentication failures
            raise
        except Exception as e:
            raise AuthenticationFailed(f"Authentication failed: {str(e)}")
    
    def logout(self, refresh_token: str) -> bool:
        """
        Logout a user by blacklisting their refresh token.
        
        Args:
            refresh_token: The refresh token to blacklist
            
        Returns:
            True if logout was successful, False otherwise
        """
        return self.token_service.blacklist_token(refresh_token)
    
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
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token to use
            
        Returns:
            Dictionary containing the new tokens
            
        Raises:
            Exception: If token refresh fails
        """
        # Validate the refresh token
        token_data = self.validate_token(refresh_token, 'refresh')
        
        # Get the user from the token
        user_id = token_data.get('user_id')
        if not user_id:
            raise AuthenticationFailed("Invalid refresh token")
            
        try:
            user = User.objects.get(uuid=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")
            
        # Generate new tokens
        return self.token_service.generate_tokens(user)