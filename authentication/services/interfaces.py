from abc import ABC, abstractmethod
from typing import Dict, Any

from django.contrib.auth import get_user_model

User = get_user_model()

class TokenServiceInterface(ABC):
    """
    Interface for token services.
    Follows the Dependency Inversion Principle by defining an abstraction
    that high-level modules can depend on.
    """
    
    @abstractmethod
    def generate_tokens(self, user: User) -> Dict[str, str]:
        """
        Generate authentication tokens for a user.
        
        Args:
            user: The user to generate tokens for
            
        Returns:
            Dictionary containing the generated tokens
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def blacklist_token(self, token: str) -> bool:
        """
        Blacklist a token to prevent its future use.
        
        Args:
            token: The token to blacklist
            
        Returns:
            True if blacklisting was successful, False otherwise
        """
        pass