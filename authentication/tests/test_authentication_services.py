from unittest import mock
from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed

from authentication.models import CustomUser
from authentication.services import TokenService, GoogleAuthService

class TokenServiceTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='test@example.com')
        self.token_service = TokenService()
    
    def test_generate_tokens(self):
        """Test token generation."""
        tokens = self.token_service.generate_tokens(self.user)
        
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertTrue(isinstance(tokens['access'], str))
        self.assertTrue(isinstance(tokens['refresh'], str))

class GoogleAuthServiceTests(TestCase):
    def setUp(self):
        self.token_service = mock.MagicMock()
        self.token_service.generate_tokens.return_value = {
            'access': 'mock_access_token',
            'refresh': 'mock_refresh_token'
        }
        
        self.auth_service = GoogleAuthService(self.token_service)
        
        # Sample user info from Google
        self.mock_user_info = {
            'sub': 'google_id_12345',
            'email': 'test@example.com',
            'given_name': 'Test',
            'family_name': 'User'
        }
    
    @mock.patch('authentication.services.id_token.verify_oauth2_token')
    def test_verify_google_token_success(self, mock_verify):
        """Test successful token verification."""
        mock_verify.return_value = self.mock_user_info
        
        result = self.auth_service.verify_google_token('valid_token')
        
        self.assertEqual(result, self.mock_user_info)
        mock_verify.assert_called_once()
    
    @mock.patch('authentication.services.id_token.verify_oauth2_token')
    def test_verify_google_token_empty(self, mock_verify):
        """Test token verification with empty token."""

        with self.assertRaises(AuthenticationFailed):
            self.auth_service.verify_google_token('')
        
        mock_verify.assert_not_called()
    
    @mock.patch('authentication.services.id_token.verify_oauth2_token')
    def test_verify_google_token_invalid(self, mock_verify):
        """Test token verification with invalid token."""
        mock_verify.side_effect = ValueError("Invalid token")
        
        with self.assertRaises(AuthenticationFailed):
            self.auth_service.verify_google_token('invalid_token')
        
        mock_verify.assert_called_once()
    
    @mock.patch('authentication.services.id_token.verify_oauth2_token')
    def test_verify_google_token_returns_none(self, mock_verify):
        """Test token verification that returns None."""
        mock_verify.return_value = None
        
        with self.assertRaises(AuthenticationFailed):
            self.auth_service.verify_google_token('token')
        
        mock_verify.assert_called_once()
    
    def test_authenticate_or_create_user_invalid_info(self):
        """Test authentication with invalid user info."""
        with self.assertRaises(AuthenticationFailed):
            self.auth_service.authenticate_or_create_user({})
    
    def test_authenticate_or_create_user_no_email(self):
        """Test authentication with missing email."""
        user_info = {'sub': 'google_id_12345'}
        
        with self.assertRaises(AuthenticationFailed):
            self.auth_service.authenticate_or_create_user(user_info)
    
    def test_authenticate_or_create_user_existing_by_google_id(self):
        """Test finding existing user by Google ID."""

        # Create a user with the Google ID
        existing_user = CustomUser.objects.create_user(
            email='existing@example.com',
            google_id=self.mock_user_info['sub']
        )
        
        user, is_new_user = self.auth_service.authenticate_or_create_user(self.mock_user_info)
        
        self.assertEqual(user.uuid, existing_user.uuid)
        self.assertFalse(is_new_user)
    
    def test_authenticate_or_create_user_existing_by_email(self):
        """Test finding existing user by email and updating Google ID."""

        # Create a user with the same email but no Google ID
        existing_user = CustomUser.objects.create_user(
            email=self.mock_user_info['email']
        )
        
        user, is_new_user = self.auth_service.authenticate_or_create_user(self.mock_user_info)
        
        self.assertEqual(user.uuid, existing_user.uuid)
        self.assertEqual(user.google_id, self.mock_user_info['sub'])
        self.assertFalse(is_new_user)
    
    def test_authenticate_or_create_user_new_user(self):
        """Test creating a new user."""
        user, is_new_user = self.auth_service.authenticate_or_create_user(self.mock_user_info)
        
        self.assertEqual(user.email, self.mock_user_info['email'])
        self.assertEqual(user.google_id, self.mock_user_info['sub'])
        self.assertEqual(user.first_name, self.mock_user_info['given_name'])
        self.assertEqual(user.last_name, self.mock_user_info['family_name'])
        self.assertTrue(is_new_user)
    
    @mock.patch.object(GoogleAuthService, 'verify_google_token')
    @mock.patch.object(GoogleAuthService, 'authenticate_or_create_user')
    def test_process_google_login(self, mock_authenticate, mock_verify):
        """Test the complete login process."""
        mock_verify.return_value = self.mock_user_info
        
        user = CustomUser.objects.create_user(
            email=self.mock_user_info['email'],
            google_id=self.mock_user_info['sub']
        )
        mock_authenticate.return_value = (user, False)
        
        result = self.auth_service.process_google_login('valid_token')
        
        self.assertEqual(result['user'], user)
        self.assertEqual(result['tokens'], self.token_service.generate_tokens.return_value)
        self.assertFalse(result['is_new_user'])
        
        mock_verify.assert_called_once_with('valid_token')
        mock_authenticate.assert_called_once_with(self.mock_user_info)
        self.token_service.generate_tokens.assert_called_once_with(user)