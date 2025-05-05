from typing import Dict, Any
import logging

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError

from authentication.services.interfaces import TokenServiceInterface

User = get_user_model()

class JWTTokenService(TokenServiceInterface):
    def generate_tokens(self, user: User) -> Dict[str, str]:
        """
        Generate JWT tokens for a user.
        
        Args:
            user: The user to generate tokens for
            
        Returns:
            Dictionary containing access and refresh tokens
        """
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims to the token
        refresh['user_id'] = str(user.uuid)
        refresh['email'] = user.email
        refresh['username'] = user.username
        refresh['role'] = user.role
        
        # Add additional fields if available
        if hasattr(user, 'npm') and user.npm:
            refresh['npm'] = user.npm

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    
    def validate_token(self, token: str, token_type: str = 'access') -> Dict[str, Any]:
        """
        Validate a JWT token and return its payload.
        
        Args:
            token: The token to validate
            token_type: The type of token ('access' or 'refresh')
            
        Returns:
            Dictionary containing the token payload
            
        Raises:
            TokenError: If token validation fails
        """
        from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, UntypedToken
        
        try:
            if token_type == 'access':
                token_obj = AccessToken(token)
            elif token_type == 'refresh':
                token_obj = RefreshToken(token)
            else:
                token_obj = UntypedToken(token)
                
            # Check if token is blacklisted
            if token_type == 'refresh':
                jti = token_obj.get('jti')
                if BlacklistedToken.objects.filter(token__jti=jti).exists():
                    raise TokenError('Token is blacklisted')
                
            # Valid token - return payload
            return {k: v for k, v in token_obj.payload.items()}
            
        except TokenError as e:
            raise
        except Exception as e:
            raise TokenError(f"Token validation failed: {str(e)}")
    
    def blacklist_token(self, token: str) -> bool:
        """
        Blacklist a refresh token.
        
        Args:
            token: The refresh token to blacklist
            
        Returns:
            True if blacklisting was successful, False otherwise
        """
        try:
            # Create a RefreshToken instance
            token_obj = RefreshToken(token)
            
            # Add to blacklist
            token_obj.blacklist()
            
            return True
            
        except TokenError as e:
            return False
        except Exception as e:
            return False