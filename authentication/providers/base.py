from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple, Any

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class AuthenticationProvider(ABC):
    """
    Abstract base class for all authentication providers.
    
    Follows the Strategy pattern, allowing different authentication
    strategies to be implemented with a consistent interface.
    """
    
    @abstractmethod
    def authenticate(self, credential: str) -> Tuple[User, bool]:
        """
        Authenticate a user with the given credential.
        
        Args:
            credential: The authentication credential specific to this provider
            
        Returns:
            Tuple containing:
                - User: The authenticated user
                - bool: True if this is a new user, False otherwise
                
        Raises:
            AuthenticationFailed: If authentication fails
        """
        pass
    
    @abstractmethod
    def validate_credential(self, credential: str) -> Dict[str, Any]:
        """
        Validate the provided credential and return user info.
        
        Args:
            credential: The authentication credential to validate
            
        Returns:
            Dict containing user information extracted from the credential
            
        Raises:
            AuthenticationFailed: If credential validation fails
        """
        pass
    
    def get_or_create_user(self, user_info: Dict[str, Any]) -> Tuple[User, bool]:
        """
        Get an existing user or create a new one based on the provided info.
        
        Args:
            user_info: Dictionary containing user information
            
        Returns:
            Tuple containing:
                - User: The retrieved or created user
                - bool: True if a new user was created, False otherwise
        """
        raise NotImplementedError(
            "Each provider must implement its own user retrieval/creation logic"
        )