from unittest import mock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from authentication.models import CustomUser
from authentication.services import GoogleAuthService

class GoogleLoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('authentication:google_login')
        
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            google_id='google_id_12345'
        )
        
        # Mock tokens
        self.mock_tokens = {
            'access': 'mock_access_token',
            'refresh': 'mock_refresh_token'
        }
        
        # Patch GoogleAuthService.process_google_login
        self.process_patch = mock.patch.object(
            GoogleAuthService, 
            'process_google_login',
            return_value={
                'user': self.user,
                'tokens': self.mock_tokens,
                'is_new_user': False
            }
        )
        self.mock_process = self.process_patch.start()
        self.addCleanup(self.process_patch.stop)
    
    def test_google_login_success(self):
        """Test successful Google login."""
        response = self.client.post(
            self.url, 
            {'id_token': 'valid_token'}, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['access_token'], self.mock_tokens['access'])
        self.assertEqual(response.data['refresh_token'], self.mock_tokens['refresh'])
        self.assertEqual(response.data['data']['email'], self.user.email)
        self.assertEqual(response.data['detail'], "Successfully logged in.")
        
        self.mock_process.assert_called_once_with('valid_token')
    
    def test_google_login_new_user(self):
        """Test Google login with new user creation."""

        # Update the mock to return a new user
        self.mock_process.return_value = {
            'user': self.user,
            'tokens': self.mock_tokens,
            'is_new_user': True
        }
        
        response = self.client.post(
            self.url, 
            {'id_token': 'valid_token'}, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Successfully registered and logged in.")
    
    def test_google_login_missing_token(self):
        """Test Google login with missing token."""
        response = self.client.post(
            self.url, 
            {}, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('id_token', response.data)

        self.mock_process.assert_not_called()
    
    def test_google_login_empty_token(self):
        """Test Google login with empty token."""
        response = self.client.post(
            self.url, 
            {'id_token': ''}, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('id_token', response.data)
        
        self.mock_process.assert_not_called()
    
    @mock.patch.object(GoogleAuthService, 'process_google_login')
    def test_google_login_authentication_failed(self, mock_process):
        """Test Google login with failed authentication."""
        
        # Setup the mock to raise an exception
        mock_process.side_effect = AuthenticationFailed("Invalid token")
        
        response = self.client.post(
            self.url, 
            {'id_token': 'invalid_token'}, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], "Invalid token")
        
        mock_process.assert_called_once_with('invalid_token')
    
    @mock.patch.object(GoogleAuthService, 'process_google_login')
    def test_google_login_server_error(self, mock_process):
        """Test Google login with server error."""
        
        # Setup the mock to raise an unexpected exception
        mock_process.side_effect = Exception("Unexpected error")
        
        response = self.client.post(
            self.url, 
            {'id_token': 'valid_token'}, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        mock_process.assert_called_once_with('valid_token')
    
    def test_google_login_invalid_response_data(self):
        """Test Google login with invalid response data structure."""

        # Mock the process_google_login to return invalid data
        self.mock_process.return_value = {
            'user': self.user,
            'tokens': {'access': None, 'refresh': None},
            'is_new_user': False
        }
        
        response = self.client.post(
            self.url, 
            {'id_token': 'valid_token'}, 
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_google_login_parse_error(self):
        """Test Google login with malformed JSON data."""
        # Create malformed request by sending invalid JSON
        response = self.client.post(
            self.url,
            data="invalid json data{",  # Malformed JSON
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.mock_process.assert_not_called()