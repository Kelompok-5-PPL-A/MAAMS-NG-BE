from typing import Dict, Type
import logging

from authentication.providers.base import AuthenticationProvider
from authentication.providers.google import GoogleAuthProvider
from authentication.providers.sso_ui import SSOUIAuthProvider

logger = logging.getLogger(__name__)

class AuthProviderFactory:
    """
    Factory for creating authentication provider instances.
    
    Follows the Factory pattern, allowing the system to create
    different authentication providers without specifying the exact class.
    """
    
    _providers: Dict[str, Type[AuthenticationProvider]] = {
        'google': GoogleAuthProvider,
        'sso': SSOUIAuthProvider,
    }
    
    @classmethod
    def get_provider(cls, provider_type: str) -> AuthenticationProvider:
        """
        Get an authentication provider instance based on type.
        
        Args:
            provider_type: The type of authentication provider to create
            
        Returns:
            An instance of the requested authentication provider
            
        Raises:
            ValueError: If the requested provider type doesn't exist
        """
        provider_class = cls._providers.get(provider_type.lower())
        
        if not provider_class:
            logger.error(f"Requested unknown auth provider: {provider_type}")
            raise ValueError(f"Unknown authentication provider: {provider_type}")
            
        return provider_class()
    
    @classmethod
    def register_provider(cls, provider_type: str, provider_class: Type[AuthenticationProvider]) -> None:
        """
        Register a new authentication provider.
        
        Args:
            provider_type: The type identifier for the provider
            provider_class: The provider class to register
        """
        cls._providers[provider_type.lower()] = provider_class
        logger.info(f"Registered new auth provider: {provider_type}")
    
    @classmethod
    def get_available_providers(cls) -> list:
        """
        Get a list of available provider types.
        
        Returns:
            List of available provider type names
        """
        return list(cls._providers.keys())