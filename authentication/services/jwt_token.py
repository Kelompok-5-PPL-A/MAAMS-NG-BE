import jwt
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings

from authentication.services.interfaces import TokenServiceInterface
from authentication.models import CustomUser

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

def create_token(user: CustomUser, token_type: str = "access_token") -> str:
    """
    Create a JWT token for the given user.
    
    Args:
        user: The user to create the token for
        token_type: The type of token to create (access_token or refresh_token)
        
    Returns:
        The encoded JWT token
    """
    exp_time = (
        settings.ACCESS_TOKEN_EXP_TIME
        if token_type == "access_token"
        else settings.REFRESH_TOKEN_EXP_TIME
    )
    
    secret_key = (
        settings.ACCESS_TOKEN_SECRET_KEY
        if token_type == "access_token"
        else settings.REFRESH_TOKEN_SECRET_KEY
    )
    
    payload = {
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=exp_time),
        "user_id": str(user.uuid),
        "username": user.username,
        "email": user.email,
        "role": user.role
    }
    
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def decode_token(token: str, token_type: str = "access_token") -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The token to decode
        token_type: The type of token (access_token or refresh_token)
        
    Returns:
        The decoded token payload if valid, None otherwise
    """
    secret_key = (
        settings.ACCESS_TOKEN_SECRET_KEY
        if token_type == "access_token"
        else settings.REFRESH_TOKEN_SECRET_KEY
    )
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        # Check if token is expired
        if "exp" in payload:
            exp_time = payload["exp"]
            if exp_time < datetime.now(timezone.utc).timestamp():
                return None
        
        return payload
    except jwt.exceptions.ExpiredSignatureError:
        return None
    except jwt.exceptions.InvalidTokenError:
        return None