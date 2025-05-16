import unittest
from unittest.mock import patch, MagicMock, ANY

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, UntypedToken

from authentication.services.auth import AuthenticationService
from authentication.services.jwt_token import JWTTokenService
from authentication.providers.factory import AuthProviderFactory
from authentication.providers.base import AuthenticationProvider

User = get_user_model()

class MockProvider(AuthenticationProvider):
    """Mock authentication provider for testing"""
    
    def __init__(self, user=None, is_new=False, raises=None):
        self.user = user
        self.is_new = is_new
        self.raises = raises
        
    def authenticate(self, credential):
        if self.raises:
            raise self.raises
        return self.user, self.is_new
        
    def validate_credential(self, credential):
        return {}
        
    def get_or_create_user(self, user_info):
        return self.user, self.is_new

class MockTokenService:
    """Mock token service for testing"""
    
    def __init__(self, tokens=None, payload=None, blacklist_result=True):
        self.tokens = tokens or {'access': 'access_token', 'refresh': 'refresh_token'}
        self.payload = payload or {}
        self.blacklist_result = blacklist_result
        
    def generate_tokens(self, user):
        return self.tokens
        
    def validate_token(self, token, token_type='access'):
        return self.payload
        
    def validate_refresh_token(self, token):
        return self.payload
        
    def create_access_token(self, payload):
        return 'new_access_token'

class TestAuthenticationService(unittest.TestCase):
    def setUp(self):
        self.mock_token_service = MockTokenService()
        self.service = AuthenticationService(self.mock_token_service)
        
        # Create a mock user
        self.mock_user = MagicMock(spec=User)
        self.mock_user.uuid = '12345678-90ab-cdef-1234-567890abcdef'
        
    @patch.object(AuthProviderFactory, 'get_provider')
    def test_authenticate_with_provider_success(self, mock_get_provider):
        """Test successful authentication"""
        # Set up the mock provider
        mock_provider = MockProvider(user=self.mock_user, is_new=False)
        mock_get_provider.return_value = mock_provider
        
        # Test authentication
        tokens, user, is_new = self.service.authenticate_with_provider('google', 'credential')
        
        # Verify results
        self.assertEqual(tokens, self.mock_token_service.tokens)
        self.assertEqual(user, self.mock_user)
        self.assertFalse(is_new)
        mock_get_provider.assert_called_once_with('google')
        
    @patch.object(AuthProviderFactory, 'get_provider')
    def test_authenticate_with_provider_new_user(self, mock_get_provider):
        """Test authentication with new user"""
        # Set up the mock provider
        mock_provider = MockProvider(user=self.mock_user, is_new=True)
        mock_get_provider.return_value = mock_provider
        
        # Test authentication
        tokens, user, is_new = self.service.authenticate_with_provider('google', 'credential')
        
        # Verify results
        self.assertEqual(tokens, self.mock_token_service.tokens)
        self.assertEqual(user, self.mock_user)
        self.assertTrue(is_new)
        
    @patch.object(AuthProviderFactory, 'get_provider')
    def test_authenticate_with_provider_auth_failed(self, mock_get_provider):
        """Test authentication with AuthenticationFailed"""
        # Set up the mock provider to raise AuthenticationFailed
        mock_provider = MockProvider(raises=AuthenticationFailed("Auth failed"))
        mock_get_provider.return_value = mock_provider
        
        # Test authentication
        with self.assertRaises(AuthenticationFailed):
            self.service.authenticate_with_provider('google', 'credential')
            
    @patch.object(AuthProviderFactory, 'get_provider')
    def test_authenticate_with_provider_other_exception(self, mock_get_provider):
        """Test authentication with other exception"""
        # Set up the mock provider to raise Exception
        mock_provider = MockProvider(raises=Exception("Other error"))
        mock_get_provider.return_value = mock_provider
        
        # Test authentication
        with self.assertRaises(AuthenticationFailed):
            self.service.authenticate_with_provider('google', 'credential')
            
    def test_logout_success(self):
        """Test successful logout"""
        # Test logout
        success = self.service.logout('refresh_token')
        
        # Verify result
        self.assertTrue(success)
        
    def test_logout_failure(self):
        """Test failed logout"""
        # Set up mock token service to fail validation
        self.service.token_service = MockTokenService()
        self.service.token_service.validate_refresh_token = MagicMock(side_effect=TokenError("Invalid token"))
        
        # Test logout
        success = self.service.logout('refresh_token')
        
        # Verify result
        self.assertFalse(success)
        
    def test_validate_token(self):
        """Test validating a token"""
        # Set up mock token service with specific payload
        expected_payload = {'user_id': '12345', 'exp': 1000000000}
        self.service.token_service = MockTokenService(payload=expected_payload)
        
        # Test token validation
        payload = self.service.validate_token('token', 'access')
        
        # Verify result
        self.assertEqual(payload, expected_payload)
        
    def test_refresh_token_success(self):
        """Test successful token refresh"""
        # Set up mock token service
        token_payload = {'user_id': str(self.mock_user.uuid)}
        self.service.token_service = MockTokenService(payload=token_payload)
        
        # Test token refresh
        tokens = self.service.refresh_token('refresh_token')
        
        # Verify results
        self.assertEqual(tokens, {'access': 'new_access_token'})
        
    def test_refresh_token_failure(self):
        """Test token refresh failure"""
        # Set up mock token service to raise TokenError
        self.service.token_service = MockTokenService()
        self.service.token_service.validate_refresh_token = MagicMock(side_effect=TokenError("Invalid token"))
        
        # Test token refresh
        with self.assertRaises(AuthenticationFailed):
            self.service.refresh_token('invalid_token')

class TestJWTTokenService(unittest.TestCase):
    def setUp(self):
        self.service = JWTTokenService()
        
        # Create a mock user
        self.mock_user = MagicMock(spec=User)
        self.mock_user.uuid = '12345678-90ab-cdef-1234-567890abcdef'
        self.mock_user.email = 'test@example.com'
        self.mock_user.username = 'testuser'
        self.mock_user.role = 'user'
        self.mock_user.npm = '2206081534'
        
    @patch('authentication.services.jwt_token.RefreshToken')
    def test_generate_tokens(self, mock_refresh_token_class):
        """Test generating JWT tokens"""
        # Set up mock RefreshToken
        mock_refresh = MagicMock()
        mock_refresh.access_token = MagicMock()
        mock_refresh.__str__.return_value = 'refresh_token'
        mock_refresh.access_token.__str__.return_value = 'access_token'
        mock_refresh_token_class.for_user.return_value = mock_refresh
        
        # Test token generation
        tokens = self.service.generate_tokens(self.mock_user)
        
        # Verify results
        self.assertEqual(tokens, {'access': 'access_token', 'refresh': 'refresh_token'})
        mock_refresh_token_class.for_user.assert_called_once_with(self.mock_user)
        
    @patch('authentication.services.jwt_token.jwt.decode')
    def test_validate_access_token(self, mock_jwt_decode):
        """Test validating an access token"""
        # Set up mock jwt.decode
        expected_payload = {'sub': 'subject', 'exp': 1000000000}
        mock_jwt_decode.return_value = expected_payload
        
        # Test token validation
        payload = self.service.validate_token('token', 'access')
        
        # Verify results
        self.assertEqual(payload, expected_payload)
        mock_jwt_decode.assert_called_once_with(
            'token', 
            self.service.signing_key, 
            algorithms=[self.service.algorithm]
        )
        
    @patch('authentication.services.jwt_token.jwt.decode')
    def test_validate_refresh_token(self, mock_jwt_decode):
        """Test validating a refresh token"""
        # Set up mock jwt.decode
        expected_payload = {'sub': 'subject', 'exp': 1000000000}
        mock_jwt_decode.return_value = expected_payload
        
        # Test token validation
        payload = self.service.validate_refresh_token('token')
        
        # Verify results
        self.assertEqual(payload, expected_payload)
        mock_jwt_decode.assert_called_once_with(
            'token', 
            self.service.signing_key, 
            algorithms=[self.service.algorithm]
        )
        
    @patch('authentication.services.jwt_token.jwt.decode')
    def test_validate_untyped_token(self, mock_jwt_decode):
        """Test validating an untyped token"""
        # Set up mock jwt.decode
        expected_payload = {'sub': 'subject', 'exp': 1000000000}
        mock_jwt_decode.return_value = expected_payload
        
        # Test token validation
        payload = self.service.validate_token('token', 'untyped')
        
        # Verify results
        self.assertEqual(payload, expected_payload)
        mock_jwt_decode.assert_called_once_with(
            'token', 
            self.service.signing_key, 
            algorithms=[self.service.algorithm]
        )
        
    @patch('authentication.services.jwt_token.jwt.decode')
    def test_validate_token_error(self, mock_jwt_decode):
        """Test token validation with TokenError"""
        # Set up mock jwt.decode to raise jwt.InvalidTokenError
        import jwt as pyjwt
        mock_jwt_decode.side_effect = pyjwt.InvalidTokenError("Token error")
        
        # Test token validation
        with self.assertRaises(TokenError):
            self.service.validate_token('token', 'access')
            
    @patch('authentication.services.jwt_token.jwt.decode')
    def test_validate_token_expired(self, mock_jwt_decode):
        """Test token validation with ExpiredSignatureError"""
        # Set up mock jwt.decode to raise jwt.ExpiredSignatureError
        import jwt as pyjwt
        mock_jwt_decode.side_effect = pyjwt.ExpiredSignatureError()
        
        # Test token validation
        with self.assertRaises(TokenError):
            self.service.validate_token('token', 'access')
        
    @patch('authentication.services.jwt_token.jwt.decode')
    def test_blacklist_token_token_error(self, mock_jwt_decode):
        """Test blacklisting a token with TokenError"""
        # Set up mock jwt.decode to raise jwt.InvalidTokenError
        import jwt as pyjwt
        mock_jwt_decode.side_effect = pyjwt.InvalidTokenError("Token error")
        
        # Test blacklisting
        success = self.service.blacklist_token('token')
        
        # Verify results
        self.assertFalse(success)