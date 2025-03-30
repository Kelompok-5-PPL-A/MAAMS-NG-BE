import unittest
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError

from authentication.services.auth_service import AuthenticationService
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
        
    def blacklist_token(self, token):
        return self.blacklist_result

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
        # Set up mock token service to fail on blacklist
        self.service.token_service = MockTokenService(blacklist_result=False)
        
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
        expected_tokens = {'access': 'new_access', 'refresh': 'new_refresh'}
        
        self.service.token_service = MockTokenService(
            payload=token_payload,
            tokens=expected_tokens
        )
        
        # Mock User.objects.get
        with patch('authentication.services.auth_service.User.objects.get') as mock_get:
            mock_get.return_value = self.mock_user
            
            # Test token refresh
            tokens = self.service.refresh_token('refresh_token')
            
            # Verify results
            self.assertEqual(tokens, expected_tokens)
            mock_get.assert_called_once_with(uuid=self.mock_user.uuid)
            
    def test_refresh_token_missing_user_id(self):
        """Test token refresh with missing user_id claim"""
        # Set up mock token service with no user_id in payload
        self.service.token_service = MockTokenService(payload={})
        
        # Test token refresh
        with self.assertRaises(AuthenticationFailed):
            self.service.refresh_token('refresh_token')
            
    def test_refresh_token_user_not_found(self):
        """Test token refresh with user not found"""
        # Set up mock token service
        token_payload = {'user_id': 'non_existent_id'}
        self.service.token_service = MockTokenService(payload=token_payload)
        
        # Mock User.objects.get to raise DoesNotExist
        with patch('authentication.services.auth_service.User.objects.get') as mock_get:
            mock_get.side_effect = User.DoesNotExist
            
            # Test token refresh
            with self.assertRaises(AuthenticationFailed):
                self.service.refresh_token('refresh_token')
                
                
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
        self.mock_user.noWA = '08123456789'
        
    @patch('authentication.services.jwt_token.RefreshToken')
    def test_generate_tokens(self, mock_refresh_token):
        """Test generating JWT tokens"""
        # Set up mock RefreshToken
        mock_refresh = MagicMock()
        mock_refresh.access_token = MagicMock()
        mock_refresh.__str__.return_value = 'refresh_token'
        mock_refresh.access_token.__str__.return_value = 'access_token'
        mock_refresh_token.for_user.return_value = mock_refresh
        
        # Test token generation
        tokens = self.service.generate_tokens(self.mock_user)
        
        # Verify results
        self.assertEqual(tokens, {'access': 'access_token', 'refresh': 'refresh_token'})
        mock_refresh_token.for_user.assert_called_once_with(self.mock_user)
        
        # Verify custom claims were added
        self.assertEqual(mock_refresh['user_id'], str(self.mock_user.uuid))
        self.assertEqual(mock_refresh['email'], self.mock_user.email)
        self.assertEqual(mock_refresh['username'], self.mock_user.username)
        self.assertEqual(mock_refresh['role'], self.mock_user.role)
        self.assertEqual(mock_refresh['npm'], self.mock_user.npm)
        self.assertEqual(mock_refresh['noWA'], self.mock_user.noWA)
        
    @patch('authentication.services.jwt_token.AccessToken')
    def test_validate_access_token(self, mock_access_token):
        """Test validating an access token"""
        # Set up mock AccessToken
        mock_token = MagicMock()
        mock_token.payload = {'sub': 'subject', 'exp': 1000000000}
        mock_access_token.return_value = mock_token
        
        # Test token validation
        payload = self.service.validate_token('token', 'access')
        
        # Verify results
        self.assertEqual(payload, mock_token.payload)
        mock_access_token.assert_called_once_with('token')
        
    @patch('authentication.services.jwt_token.RefreshToken')
    def test_validate_refresh_token(self, mock_refresh_token):
        """Test validating a refresh token"""
        # Set up mock RefreshToken
        mock_token = MagicMock()
        mock_token.payload = {'sub': 'subject', 'exp': 1000000000}
        mock_token.get.return_value = 'jti_value'
        mock_refresh_token.return_value = mock_token
        
        # Mock BlacklistedToken.objects.filter
        with patch('authentication.services.jwt_token.BlacklistedToken.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            
            # Test token validation
            payload = self.service.validate_token('token', 'refresh')
            
            # Verify results
            self.assertEqual(payload, mock_token.payload)
            mock_refresh_token.assert_called_once_with('token')
            mock_token.get.assert_called_once_with('jti')
            mock_filter.assert_called_once_with(token__jti='jti_value')
            
    @patch('authentication.services.jwt_token.RefreshToken')
    def test_validate_refresh_token_blacklisted(self, mock_refresh_token):
        """Test validating a blacklisted refresh token"""
        # Set up mock RefreshToken
        mock_token = MagicMock()
        mock_token.get.return_value = 'jti_value'
        mock_refresh_token.return_value = mock_token
        
        # Mock BlacklistedToken.objects.filter
        with patch('authentication.services.jwt_token.BlacklistedToken.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = True
            
            # Test token validation
            with self.assertRaises(TokenError):
                self.service.validate_token('token', 'refresh')
                
    @patch('authentication.services.jwt_token.UntypedToken')
    def test_validate_untyped_token(self, mock_untyped_token):
        """Test validating an untyped token"""
        # Set up mock UntypedToken
        mock_token = MagicMock()
        mock_token.payload = {'sub': 'subject', 'exp': 1000000000}
        mock_untyped_token.return_value = mock_token
        
        # Test token validation
        payload = self.service.validate_token('token', 'untyped')
        
        # Verify results
        self.assertEqual(payload, mock_token.payload)
        mock_untyped_token.assert_called_once_with('token')
        
    @patch('authentication.services.jwt_token.AccessToken')
    def test_validate_token_error(self, mock_access_token):
        """Test token validation with TokenError"""
        # Set up mock AccessToken to raise TokenError
        mock_access_token.side_effect = TokenError("Token error")
        
        # Test token validation
        with self.assertRaises(TokenError):
            self.service.validate_token('token', 'access')
            
    @patch('authentication.services.jwt_token.AccessToken')
    def test_validate_token_other_exception(self, mock_access_token):
        """Test token validation with other exception"""
        # Set up mock AccessToken to raise Exception
        mock_access_token.side_effect = Exception("Other error")
        
        # Test token validation
        with self.assertRaises(TokenError):
            self.service.validate_token('token', 'access')
            
    @patch('authentication.services.jwt_token.RefreshToken')
    def test_blacklist_token_success(self, mock_refresh_token):
        """Test blacklisting a token successfully"""
        # Set up mock RefreshToken
        mock_token = MagicMock()
        mock_token.__getitem__.return_value = 'jti_value'
        mock_refresh_token.return_value = mock_token
        
        # Test blacklisting
        success = self.service.blacklist_token('token')
        
        # Verify results
        self.assertTrue(success)
        mock_refresh_token.assert_called_once_with('token')
        mock_token.blacklist.assert_called_once()
        
    @patch('authentication.services.jwt_token.RefreshToken')
    def test_blacklist_token_token_error(self, mock_refresh_token):
        """Test blacklisting a token with TokenError"""
        # Set up mock RefreshToken to raise TokenError
        mock_refresh_token.side_effect = TokenError("Token error")
        
        # Test blacklisting
        success = self.service.blacklist_token('token')
        
        # Verify results
        self.assertFalse(success)
        
    @patch('authentication.services.jwt_token.RefreshToken')
    def test_blacklist_token_other_exception(self, mock_refresh_token):
        """Test blacklisting a token with other exception"""
        # Set up mock RefreshToken to raise Exception
        mock_refresh_token.side_effect = Exception("Other error")
        
        # Test blacklisting
        success = self.service.blacklist_token('token')
        
        # Verify results
        self.assertFalse(success)