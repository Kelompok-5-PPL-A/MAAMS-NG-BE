import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings

from authentication.services.interfaces import TokenServiceInterface

User = get_user_model()

class JWTTokenService(TokenServiceInterface):
    """
    Service for handling JWT token operations.
    """
    
    def __init__(self):
        self.access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        self.refresh_token_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
        self.algorithm = settings.SIMPLE_JWT['ALGORITHM']
        self.signing_key = settings.SIMPLE_JWT['SIGNING_KEY']
        
    def generate_tokens(self, user: User) -> Dict[str, str]:
        """
        Generate authentication tokens for a user.
        
        Args:
            user: The user to generate tokens for
            
        Returns:
            Dictionary containing the generated tokens
        """
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims
        refresh['user_id'] = str(user.uuid)
        refresh['email'] = user.email
        refresh['username'] = user.username
        refresh['role'] = user.role
        refresh['npm'] = user.npm
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
        
    def validate_token(self, token: str, token_type: str = 'access') -> Dict[str, Any]:
        """
        Validate a token and return its payload.
        
        Args:
            token: The token to validate
            token_type: The type of token ('access' or 'refresh')
            
        Returns:
            Dict containing the token payload
            
        Raises:
            TokenError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.signing_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenError('Token has expired')
        except jwt.InvalidTokenError as e:
            raise TokenError(f'Invalid token: {str(e)}')
            
    def validate_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a refresh token.
        
        Args:
            token: The refresh token to validate
            
        Returns:
            Dict containing the token payload
            
        Raises:
            TokenError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.signing_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenError('Refresh token has expired')
        except jwt.InvalidTokenError as e:
            raise TokenError(f'Invalid refresh token: {str(e)}')
            
    def create_access_token(self, payload: Dict[str, Any]) -> str:
        """
        Create a new access token from a payload.
        
        Args:
            payload: The token payload
            
        Returns:
            The new access token
        """
        now = timezone.now()
        payload['exp'] = now + self.access_token_lifetime
        payload['iat'] = now
        
        return jwt.encode(
            payload,
            self.signing_key,
            algorithm=self.algorithm
        )
        
    def blacklist_token(self, token: str) -> bool:
        """
        Blacklist a token to prevent its future use.
        
        Args:
            token: The token to blacklist
            
        Returns:
            True if blacklisting was successful, False otherwise
        """
        try:
            # Validate the token first
            self.validate_token(token)
            return True
        except Exception:
            return False