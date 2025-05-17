import unittest
from unittest.mock import patch, MagicMock, ANY

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed, ParseError

from authentication.providers.base import AuthenticationProvider
from authentication.providers.factory import AuthProviderFactory
from authentication.providers.google import GoogleAuthProvider
from authentication.providers.sso_ui import SSOUIAuthProvider

User = get_user_model()

class MockAuthProvider(AuthenticationProvider):
    """Mock provider for testing the factory"""
    
    def authenticate(self, credential):
        return None, False
        
    def validate_credential(self, credential):
        return {}

class TestAuthProviderFactory(unittest.TestCase):
    def test_get_provider_google(self):
        """Test getting a Google provider"""
        provider = AuthProviderFactory.get_provider('google')
        self.assertIsInstance(provider, GoogleAuthProvider)
        
    @patch('authentication.providers.sso_ui.SSOJWTConfig')
    def test_get_provider_sso(self, mock_config_class):
        """Test getting an SSO provider"""
        # Mock the config
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        
        # Get provider
        provider = AuthProviderFactory.get_provider('sso')
        self.assertIsInstance(provider, SSOUIAuthProvider)
        
    def test_get_provider_case_insensitive(self):
        """Test that provider type is case insensitive"""
        provider = AuthProviderFactory.get_provider('GOOGLE')
        self.assertIsInstance(provider, GoogleAuthProvider)
        
    def test_get_provider_unknown(self):
        """Test error when getting an unknown provider"""
        with self.assertRaises(ValueError):
            AuthProviderFactory.get_provider('unknown')
            
    def test_register_provider(self):
        """Test registering a new provider"""
        AuthProviderFactory.register_provider('mock', MockAuthProvider)
        provider = AuthProviderFactory.get_provider('mock')
        self.assertIsInstance(provider, MockAuthProvider)
        
    def test_get_available_providers(self):
        """Test getting list of available providers"""
        # Make sure our mock provider is registered
        AuthProviderFactory.register_provider('mock', MockAuthProvider)
        
        providers = AuthProviderFactory.get_available_providers()
        self.assertIn('google', providers)
        self.assertIn('sso', providers)
        self.assertIn('mock', providers)

class TestGoogleAuthProvider(unittest.TestCase):
    def setUp(self):
        self.provider = GoogleAuthProvider()
        
    @patch('authentication.providers.google.id_token')
    def test_validate_credential_success(self, mock_id_token):
        """Test successful validation of Google token"""
        # Mock the Google token verification
        mock_user_info = {
            'sub': '123456789',
            'email': 'test@example.com',
            'given_name': 'Test',
            'family_name': 'User'
        }
        mock_id_token.verify_oauth2_token.return_value = mock_user_info
        
        # Test the validation
        result = self.provider.validate_credential('valid_token')
        
        # Verify results
        self.assertEqual(result, mock_user_info)
        mock_id_token.verify_oauth2_token.assert_called_once()
        
    def test_validate_credential_missing(self):
        """Test validation with missing credential"""
        with self.assertRaises(ParseError):
            self.provider.validate_credential('')
            
    @patch('authentication.providers.google.id_token')
    def test_validate_credential_missing_sub(self, mock_id_token):
        """Test validation with missing sub field"""
        # Mock the Google token verification
        mock_user_info = {
            'email': 'test@example.com'
        }
        mock_id_token.verify_oauth2_token.return_value = mock_user_info
        
        # Test the validation
        with self.assertRaises(AuthenticationFailed):
            self.provider.validate_credential('token')
            
    @patch('authentication.providers.google.id_token')
    def test_validate_credential_missing_email(self, mock_id_token):
        """Test validation with missing email field"""
        # Mock the Google token verification
        mock_user_info = {
            'sub': '123456789'
        }
        mock_id_token.verify_oauth2_token.return_value = mock_user_info
        
        # Test the validation
        with self.assertRaises(AuthenticationFailed):
            self.provider.validate_credential('token')
            
    @patch('authentication.providers.google.id_token')
    def test_validate_credential_value_error(self, mock_id_token):
        """Test validation with ValueError from Google"""
        # Mock the Google token verification to raise ValueError
        mock_id_token.verify_oauth2_token.side_effect = ValueError("Invalid token")
        
        # Test the validation
        with self.assertRaises(AuthenticationFailed):
            self.provider.validate_credential('invalid_token')
            
    @patch('authentication.providers.google.id_token')
    def test_validate_credential_unexpected_error(self, mock_id_token):
        """Test validation with unexpected error from Google"""
        # Mock the Google token verification to raise an unexpected error
        mock_id_token.verify_oauth2_token.side_effect = Exception("Unexpected error")
        
        # Test the validation
        with self.assertRaises(AuthenticationFailed):
            self.provider.validate_credential('token')
            
    @patch.object(GoogleAuthProvider, 'validate_credential')
    @patch.object(GoogleAuthProvider, 'get_or_create_user')
    def test_authenticate_success(self, mock_get_or_create, mock_validate):
        """Test successful authentication"""
        # Mock the validation and user creation
        mock_user_info = {'sub': '123', 'email': 'test@example.com'}
        mock_user = MagicMock(spec=User)
        
        mock_validate.return_value = mock_user_info
        mock_get_or_create.return_value = (mock_user, False)
        
        # Test authentication
        user, is_new = self.provider.authenticate('token')
        
        # Verify results
        self.assertEqual(user, mock_user)
        self.assertFalse(is_new)
        mock_validate.assert_called_once_with('token')
        mock_get_or_create.assert_called_once_with(mock_user_info)
        
    def test_get_or_create_user_existing_by_google_id(self):
        """Test getting existing user by Google ID"""
        # Create a mock user
        mock_user = MagicMock(spec=User)
        
        # Create a mock queryset that returns our user
        mock_queryset = MagicMock()
        mock_queryset.get.return_value = mock_user
        
        # Mock the User.objects manager
        with patch('authentication.providers.google.User.objects') as mock_objects:
            mock_objects.get.side_effect = [mock_user, User.DoesNotExist]
            
            # Test user retrieval
            user_info = {
                'sub': '123456789',
                'email': 'test@example.com',
                'given_name': 'Test',
                'family_name': 'User'
            }
            
            with patch.object(self.provider, '_update_user_if_needed') as mock_update:
                user, is_new = self.provider.get_or_create_user(user_info)
                
                # Verify results
                self.assertEqual(user, mock_user)
                self.assertFalse(is_new)
                mock_objects.get.assert_called_with(google_id='123456789')
                mock_update.assert_called_once_with(mock_user, user_info)
                
    def test_get_or_create_user_existing_by_email(self):
        """Test getting existing user by email"""
        # Create a mock user with no Google ID
        mock_user = MagicMock(spec=User)
        mock_user.google_id = None
        
        # Mock the User.objects manager
        with patch('authentication.providers.google.User.objects') as mock_objects:
            # First call raises DoesNotExist, second call returns our user
            mock_objects.get.side_effect = [User.DoesNotExist, mock_user]
            
            # Test user retrieval
            user_info = {
                'sub': '123456789',
                'email': 'test@example.com'
            }
            
            user, is_new = self.provider.get_or_create_user(user_info)
            
            # Verify results
            self.assertEqual(user, mock_user)
            self.assertFalse(is_new)
            mock_objects.get.assert_any_call(google_id='123456789')
            mock_objects.get.assert_any_call(email='test@example.com')
            
            # Check that Google ID was set
            self.assertEqual(mock_user.google_id, '123456789')
            mock_user.save.assert_called_once_with(update_fields=['google_id'])
            
    def test_get_or_create_user_new_user(self):
        """Test creating a new user"""
        # Mock the User.objects manager
        with patch('authentication.providers.google.User.objects') as mock_objects:
            mock_objects.get.side_effect = User.DoesNotExist
            
            # Mock the create_user method
            mock_new_user = MagicMock(spec=User)
            mock_objects.create_user.return_value = mock_new_user
            
            # Test user creation
            user_info = {
                'sub': '123456789',
                'email': 'test@example.com',
                'given_name': 'Test',
                'family_name': 'User'
            }
            
            with patch.object(self.provider, '_create_new_user') as mock_create:
                mock_create.return_value = mock_new_user
                user, is_new = self.provider.get_or_create_user(user_info)
                
                # Verify results
                self.assertEqual(user, mock_new_user)
                self.assertTrue(is_new)
                mock_create.assert_called_once_with(user_info)
                
    def test_create_new_user(self):
        """Test creating a new user from Google info"""
        # Mock User.objects.create_user
        mock_new_user = MagicMock(spec=User)
        
        with patch('authentication.providers.google.User.objects') as mock_objects:
            mock_objects.create_user.return_value = mock_new_user
            
            # Test user creation
            user_info = {
                'sub': '123456789',
                'email': 'test@example.com',
                'given_name': 'Test',
                'family_name': 'User'
            }
            
            user = self.provider._create_new_user(user_info)
            
            # Verify results
            self.assertEqual(user, mock_new_user)
            mock_objects.create_user.assert_called_once_with(
                email='test@example.com',
                username='test',
                google_id='123456789',
                first_name='Test',
                last_name='User',
                role='user'
            )
            
    def test_update_user_if_needed_no_updates(self):
        """Test updating user info when nothing needs updating"""
        # Create a user with all fields set
        mock_user = MagicMock(spec=User)
        mock_user.first_name = 'Existing'
        mock_user.last_name = 'User'
        
        # Test the update
        user_info = {
            'given_name': 'New',
            'family_name': 'Name'
        }
        
        self.provider._update_user_if_needed(mock_user, user_info)
        
        # Verify no updates were made
        mock_user.save.assert_not_called()
        
    def test_update_user_if_needed_with_updates(self):
        """Test updating user info when fields are empty"""
        # Create a user with empty fields
        mock_user = MagicMock(spec=User)
        mock_user.first_name = ''
        mock_user.last_name = ''
        
        # Test the update
        user_info = {
            'given_name': 'New',
            'family_name': 'Name'
        }
        
        self.provider._update_user_if_needed(mock_user, user_info)
        
        # Verify updates were made
        self.assertEqual(mock_user.first_name, 'New')
        self.assertEqual(mock_user.last_name, 'Name')
        mock_user.save.assert_called_once_with(update_fields=['first_name', 'last_name'])

class TestSSOUIAuthProvider(unittest.TestCase):
    def setUp(self):
        # Mock SSOJWTConfig
        self.config_patcher = patch('authentication.providers.sso_ui.SSOJWTConfig')
        self.mock_config_class = self.config_patcher.start()
        self.mock_config = MagicMock()
        self.mock_config_class.return_value = self.mock_config
        
        # Create provider after mocking the config
        self.provider = SSOUIAuthProvider()
        
    def tearDown(self):
        self.config_patcher.stop()
        
    @patch('authentication.providers.sso_ui.validate_ticket')
    def test_validate_credential_success(self, mock_validate_ticket):
        """Test successful validation of SSO ticket"""
        # Mock the SSO ticket validation
        mock_response = {
            "authentication_success": {
                "user": "username",
                "attributes": {
                    "npm": "2206081534",
                    "nama": "Test User"
                }
            }
        }
        mock_validate_ticket.return_value = mock_response
        
        # Test the validation
        result = self.provider.validate_credential('valid_ticket')
        
        # Verify results
        self.assertEqual(result, mock_response["authentication_success"])
        mock_validate_ticket.assert_called_once_with(self.provider.config, 'valid_ticket')
        
    def test_validate_credential_missing(self):
        """Test validation with missing credential"""
        with self.assertRaises(AuthenticationFailed):
            self.provider.validate_credential('')
            
    @patch('authentication.providers.sso_ui.validate_ticket')
    def test_validate_credential_invalid_response(self, mock_validate_ticket):
        """Test validation with invalid response"""
        # Mock the SSO ticket validation
        mock_validate_ticket.return_value = {}
        
        # Test the validation
        with self.assertRaises(AuthenticationFailed):
            self.provider.validate_credential('invalid_ticket')
            
    @patch.object(SSOUIAuthProvider, 'validate_credential')
    @patch.object(SSOUIAuthProvider, 'get_or_create_user')
    def test_authenticate_success(self, mock_get_or_create, mock_validate):
        """Test successful authentication"""
        # Mock the validation and user creation
        mock_user_info = {
            "user": "username",
            "attributes": {"npm": "2206081534"}
        }
        mock_user = MagicMock(spec=User)
        
        mock_validate.return_value = mock_user_info
        mock_get_or_create.return_value = (mock_user, False)
        
        # Test authentication
        user, is_new = self.provider.authenticate('ticket')
        
        # Verify results
        self.assertEqual(user, mock_user)
        self.assertFalse(is_new)
        mock_validate.assert_called_once_with('ticket')
        mock_get_or_create.assert_called_once_with(mock_user_info)
        
    def test_get_or_create_user_by_npm(self):
        """Test getting existing user by NPM"""
        # Create a mock user
        mock_user = MagicMock(spec=User)
        
        # Mock the User.objects manager
        with patch('authentication.providers.sso_ui.User.objects') as mock_objects:
            mock_objects.filter.return_value.first.side_effect = [
                mock_user,  # First call returns user by NPM
                None,       # Second call would be by username (not reached)
                None        # Third call would be by email (not reached)
            ]
            
            # Test user retrieval
            user_info = {
                "user": "username",
                "attributes": {
                    "npm": "2206081534",
                    "nama": "Test User"
                }
            }
            
            with patch.object(self.provider, '_update_user_info') as mock_update:
                user, is_new = self.provider.get_or_create_user(user_info)
                
                # Verify results
                self.assertEqual(user, mock_user)
                self.assertFalse(is_new)
                mock_objects.filter.assert_called_with(npm="2206081534")
                mock_update.assert_called_once()
                
    def test_get_or_create_user_by_username(self):
        """Test getting existing user by username"""
        # Create a mock user
        mock_user = MagicMock(spec=User)
        
        # Mock the User.objects manager
        with patch('authentication.providers.sso_ui.User.objects') as mock_objects:
            mock_objects.filter.return_value.first.side_effect = [
                None,       # First call returns no user by NPM
                mock_user,  # Second call returns user by username
                None        # Third call would be by email (not reached)
            ]
            
            # Test user retrieval
            user_info = {
                "user": "username",
                "attributes": {
                    "npm": "2206081534",
                    "nama": "Test User"
                }
            }
            
            with patch.object(self.provider, '_update_user_info') as mock_update:
                user, is_new = self.provider.get_or_create_user(user_info)
                
                # Verify results
                self.assertEqual(user, mock_user)
                self.assertFalse(is_new)
                mock_objects.filter.assert_any_call(npm="2206081534")
                mock_objects.filter.assert_any_call(username="username")
                mock_update.assert_called_once()
                
    def test_get_or_create_user_by_email(self):
        """Test getting existing user by email"""
        # Create a mock user
        mock_user = MagicMock(spec=User)
        
        # Mock the User.objects manager
        with patch('authentication.providers.sso_ui.User.objects') as mock_objects:
            mock_objects.filter.return_value.first.side_effect = [
                None,       # First call returns no user by NPM
                None,       # Second call returns no user by username
                mock_user   # Third call returns user by email
            ]
            
            # Test user retrieval
            user_info = {
                "user": "username",
                "attributes": {
                    "npm": "2206081534",
                    "nama": "Test User"
                }
            }
            
            with patch.object(self.provider, '_update_user_info') as mock_update:
                user, is_new = self.provider.get_or_create_user(user_info)
                
                # Verify results
                self.assertEqual(user, mock_user)
                self.assertFalse(is_new)
                mock_objects.filter.assert_any_call(npm="2206081534")
                mock_objects.filter.assert_any_call(username="username")
                mock_objects.filter.assert_any_call(email="username@ui.ac.id")
                mock_update.assert_called_once()
                
    def test_get_or_create_user_new_user(self):
        """Test creating a new user"""
        # Mock the User.objects manager
        with patch('authentication.providers.sso_ui.User.objects') as mock_objects:
            # Mock all the lookups returning None
            mock_objects.filter.return_value.first.return_value = None
            
            # Create a mock new user
            mock_new_user = MagicMock(spec=User)
            mock_objects.create_user.return_value = mock_new_user
            
            # Test user creation
            user_info = {
                "user": "username",
                "attributes": {
                    "npm": "2206081534",
                    "nama": "Test User"
                }
            }
            
            # Use the actual implementation
            user, is_new = self.provider.get_or_create_user(user_info)
            
            # Verify results
            self.assertEqual(user, mock_new_user)
            self.assertTrue(is_new)
            mock_objects.create_user.assert_called_once_with(
                username="username",
                email="username@ui.ac.id",
                npm="2206081534",
                first_name="Test",
                last_name="User",
            )
                
    def test_update_user_info_no_updates(self):
        """Test updating user info when fields are already set"""
        # Create a user with all fields set
        mock_user = MagicMock(spec=User)
        mock_user.email = "username@ui.ac.id"
        mock_user.npm = "2206081534"
        mock_user.username = "username"
        mock_user.first_name = "Existing"
        mock_user.last_name = "User"
        
        # Test the update
        self.provider._update_user_info(
            mock_user, "username", "username@ui.ac.id", "2206081534", "Existing User"
        )
        
        # Verify fields were not changed
        self.assertEqual(mock_user.email, "username@ui.ac.id")
        self.assertEqual(mock_user.npm, "2206081534")
        self.assertEqual(mock_user.username, "username")
        self.assertEqual(mock_user.first_name, "Existing")
        self.assertEqual(mock_user.last_name, "User")
        
        # Save is always called in the current implementation
        mock_user.save.assert_called_once()
        
    def test_update_user_info_with_updates(self):
        """Test updating user info when fields are empty"""
        # Create a user with empty fields
        mock_user = MagicMock(spec=User)
        mock_user.email = ""
        mock_user.npm = ""
        mock_user.first_name = ""
        mock_user.last_name = ""
        
        # Test the update
        self.provider._update_user_info(
            mock_user, "username", "username@ui.ac.id", "2206081534", "Test User"
        )
        
        # Verify updates were made
        self.assertEqual(mock_user.email, "username@ui.ac.id")
        self.assertEqual(mock_user.npm, "2206081534")
        self.assertEqual(mock_user.username, "username")
        self.assertEqual(mock_user.first_name, "Test")
        self.assertEqual(mock_user.last_name, "User")
        mock_user.save.assert_called_once()
        
    def test_update_user_info_non_ui_email(self):
        """Test update doesn't change email if it's not from UI domain"""
        # Create a user with UI email
        mock_user = MagicMock(spec=User)
        mock_user.email = "original@ui.ac.id"
        
        # Test the update with non-UI email
        self.provider._update_user_info(
            mock_user, "username", "username@gmail.com", "2206081534", "Test User"
        )
        
        # Verify email wasn't updated to non-UI domain
        self.assertEqual(mock_user.email, "original@ui.ac.id")
        mock_user.save.assert_called_once()
    
    def test_update_user_info_with_single_name(self):
        """Test updating user info with a single name"""
        # Create a user
        mock_user = MagicMock(spec=User)
        
        # Test the update with a single name (no space)
        self.provider._update_user_info(
            mock_user, "username", "username@ui.ac.id", "2206081534", "SingleName"
        )
        
        # Verify first_name and last_name are set correctly
        self.assertEqual(mock_user.first_name, "SingleName")
        self.assertEqual(mock_user.last_name, "")
        mock_user.save.assert_called_once()
            
    @patch('authentication.providers.sso_ui.validate_ticket')
    def test_validate_credential_missing_username(self, mock_validate_ticket):
        """Test validation with missing username"""
        # Mock the SSO ticket validation with missing user info
        mock_response = {
            "authentication_success": {}
        }
        mock_validate_ticket.return_value = mock_response
        
        # Test the validation
        with self.assertRaises(AuthenticationFailed):
            self.provider.validate_credential('ticket')
            
    @patch('authentication.providers.sso_ui.validate_ticket')
    def test_validate_credential_validate_ticket_error(self, mock_validate_ticket):
        """Test validation with ValidateTicketError"""
        # Mock the SSO ticket validation to raise ValidateTicketError
        from sso_ui.ticket import ValidateTicketError
        mock_validate_ticket.side_effect = ValidateTicketError("Invalid ticket")
        
        # Test the validation
        with self.assertRaises(AuthenticationFailed):
            self.provider.validate_credential('invalid_ticket')
            
    @patch('authentication.providers.sso_ui.validate_ticket')
    def test_validate_credential_unexpected_error(self, mock_validate_ticket):
        """Test validation with unexpected error"""
        # Mock the SSO ticket validation to raise an unexpected error
        mock_validate_ticket.side_effect = Exception("Unexpected error")
        
        # Test the validation
        with self.assertRaises(AuthenticationFailed):
            self.provider.validate_credential('ticket')

    def test_get_or_create_user_missing_info(self):
        """Test getting user with missing required information"""
        # Test with missing username
        user_info = {
            "attributes": {
                "npm": "2206081534",
                "nama": "Test User"
            }
        }
        
        with self.assertRaises(AuthenticationFailed) as context:
            self.provider.get_or_create_user(user_info)
        self.assertEqual(str(context.exception), "Missing required user information")
        
        # Test with missing NPM
        user_info = {
            "user": "username",
            "attributes": {
                "nama": "Test User"
            }
        }
        
        with self.assertRaises(AuthenticationFailed) as context:
            self.provider.get_or_create_user(user_info)
        self.assertEqual(str(context.exception), "Missing required user information")