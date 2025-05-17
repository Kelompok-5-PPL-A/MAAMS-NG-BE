import unittest
from unittest.mock import patch, MagicMock
import json
import os

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.http import HttpResponseRedirect

from rest_framework.test import APITestCase, APIClient, force_authenticate
from rest_framework import status
from rest_framework.request import Request
from rest_framework.exceptions import AuthenticationFailed

from authentication.views import (
    GoogleLoginView, SSOLoginView, SSOLogoutView,
    TokenRefreshView, LogoutView, UserProfileView
)
from authentication.services.auth import AuthenticationService
from authentication.services.jwt_token import JWTTokenService

User = get_user_model()

class TestGoogleLoginView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('authentication:google_login')
        
        # Create a real user for testing
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        
        # Mock id_token.verify_oauth2_token
        self.patcher1 = patch('authentication.views.id_token.verify_oauth2_token')
        self.mock_verify_oauth2_token = self.patcher1.start()
        # Configure the mock to return user info
        self.mock_user_info = {
            'sub': 'google123',
            'email': 'test@example.com',
            'given_name': 'Test',
            'family_name': 'User'
        }
        self.mock_verify_oauth2_token.return_value = self.mock_user_info
        
        # Mock token_service.generate_tokens
        self.patcher2 = patch('authentication.views.token_service.generate_tokens')
        self.mock_generate_tokens = self.patcher2.start()
        # Configure the mock to return tokens
        self.mock_tokens = {'access': 'access_token', 'refresh': 'refresh_token'}
        self.mock_generate_tokens.return_value = self.mock_tokens
        
    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        
    def test_post_success(self):
        """Test successful Google login with existing user"""
        # Make the request
        response = self.client.post(
            self.url, 
            {'id_token': 'valid_token'}, 
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['access_token'], 'access_token')
        self.assertEqual(response.data['refresh_token'], 'refresh_token')
        self.assertFalse(response.data['is_new_user'])
        
        # Verify mocks were called
        self.mock_verify_oauth2_token.assert_called_once()
        self.mock_generate_tokens.assert_called_once()
        
    def test_post_new_user(self):
        """Test Google login with a new user"""
        # Change the email to force a new user creation
        self.mock_user_info['email'] = 'newuser@example.com'
        
        # Mock User.objects.get to simulate user not found
        with patch('authentication.views.User.objects.get') as mock_get_user:
            mock_get_user.side_effect = User.DoesNotExist
            
            # Mock User.objects.create_user to return a new user
            with patch.object(GoogleLoginView, '_create_new_user') as mock_create_user:
                new_user = User.objects.create_user(
                    email='newuser@example.com',
                    username='newuser',
                    google_id='google123'
                )
                mock_create_user.return_value = new_user
                
                # Make the request
                response = self.client.post(
                    self.url, 
                    {'id_token': 'valid_token'}, 
                    format='json'
                )
                
                # Check response
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertTrue(response.data['is_new_user'])
                self.assertIn('Successfully registered', response.data['detail'])
        
    def test_post_missing_token(self):
        """Test Google login with missing ID token"""
        # Make the request without a token
        response = self.client.post(self.url, {}, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('id_token', response.data)
        
    def test_post_invalid_token(self):
        """Test Google login with invalid token"""
        # Make verify_oauth2_token raise ValueError
        self.mock_verify_oauth2_token.side_effect = ValueError("Invalid token")
        
        # Make the request
        response = self.client.post(
            self.url, 
            {'id_token': 'invalid_token'}, 
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        
    def test_post_unexpected_error(self):
        """Test Google login with unexpected error"""
        # Make verify_oauth2_token raise Exception
        self.mock_verify_oauth2_token.side_effect = Exception("Unexpected error")
        
        # Make the request
        response = self.client.post(
            self.url, 
            {'id_token': 'problem_token'}, 
            format='json'
        )
        
        # Check response - in our implementation, all exceptions are converted to AuthenticationFailed
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

class TestSSOLoginView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('authentication:sso_login')
        
        # Create a real user for testing
        self.user = User.objects.create_user(
            email='testuser@ui.ac.id',
            username='testuser',
            npm='2206081534',
            first_name='Test',
            last_name='User'
        )
        
        # Mock validate_ticket function
        self.patcher1 = patch('authentication.views.validate_ticket')
        self.mock_validate_ticket = self.patcher1.start()
        # Configure the mock to return user info
        self.mock_validation_response = {
            'authentication_success': {
                'user': 'testuser',
                'attributes': {
                    'npm': '2206081534',
                    'nama': 'Test User'
                }
            }
        }
        self.mock_validate_ticket.return_value = self.mock_validation_response
        
        # Mock token_service.generate_tokens
        self.patcher2 = patch('authentication.views.token_service.generate_tokens')
        self.mock_generate_tokens = self.patcher2.start()
        # Configure the mock to return tokens
        self.mock_tokens = {'access': 'access_token', 'refresh': 'refresh_token'}
        self.mock_generate_tokens.return_value = self.mock_tokens
        
        # Mock User.objects.filter to return the user
        self.patcher3 = patch('authentication.views.User.objects.filter')
        self.mock_filter = self.patcher3.start()
        mock_queryset = MagicMock()
        mock_queryset.first.return_value = self.user
        self.mock_filter.return_value = mock_queryset
        
    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        
    def test_get_success(self):
        """Test successful SSO login with existing user"""
        # Make the request
        response = self.client.get(f"{self.url}?ticket=valid_ticket")
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['access_token'], 'access_token')
        self.assertEqual(response.data['refresh_token'], 'refresh_token')
        self.assertFalse(response.data['is_new_user'])
        
        # Verify mocks were called
        self.mock_validate_ticket.assert_called_once()
        self.mock_generate_tokens.assert_called_once()
        
    def test_get_missing_ticket(self):
        """Test SSO login with missing ticket"""
        # Make the request without a ticket
        response = self.client.get(self.url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_get_validate_ticket_error(self):
        """Test SSO login with ticket validation error"""
        # Make validate_ticket raise ValidateTicketError
        from sso_ui.ticket import ValidateTicketError
        self.mock_validate_ticket.side_effect = ValidateTicketError("Invalid ticket")
        
        # Make the request
        response = self.client.get(f"{self.url}?ticket=invalid_ticket")
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        
    def test_get_unexpected_error(self):
        """Test SSO login with unexpected error"""
        # Make validate_ticket raise Exception
        self.mock_validate_ticket.side_effect = Exception("Unexpected error")
        
        # Make the request
        response = self.client.get(f"{self.url}?ticket=problem_ticket")
        
        # Check response - in our implementation, all exceptions are converted to AuthenticationFailed
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

class TestSSOLogoutView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = SSOLogoutView.as_view()
        
        # Create a user
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            role='admin'  # Make it an admin to pass permission check
        )
        
        # Mock SSOJWTConfig
        self.patcher = patch('authentication.views.SSOJWTConfig')
        self.mock_config_class = self.patcher.start()
        self.mock_config = MagicMock()
        self.mock_config.cas_url = 'https://cas.ui.ac.id'
        self.mock_config.service_url = 'https://example.com'
        self.mock_config_class.return_value = self.mock_config
        
    def tearDown(self):
        self.patcher.stop()
        
    def test_get(self):
        """Test SSO logout redirects correctly"""
        # Create request
        request = self.factory.get('/auth/logout-sso/')
        request.user = self.user
        
        # Add authentication to pass permission check
        force_authenticate(request, user=self.user)
        
        # Directly patch the logout function within this test
        with patch('authentication.views.logout') as mock_logout:
            # Call the view
            # Convert to a DRF Request first to match what the view uses
            drf_request = Request(request)
            drf_request.user = self.user
            with patch('rest_framework.views.Request', return_value=drf_request):
                response = self.view(request)
                
                # Check response
                self.assertIsInstance(response, HttpResponseRedirect)
                self.assertEqual(
                    response.url, 
                    f"{self.mock_config.cas_url}/logout?url={self.mock_config.service_url}"
                )
                
                # Verify logout was called with the DRF request
                mock_logout.assert_called_once_with(drf_request)

class TestTokenRefreshView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('authentication:token_refresh')
        
        # Set up mocks
        self.patcher = patch('authentication.views.auth_service')
        self.mock_auth_service = self.patcher.start()
        
        # Mock auth_service.refresh_token
        self.mock_tokens = {'access': 'new_access_token', 'refresh': 'new_refresh_token'}
        self.mock_auth_service.refresh_token.return_value = self.mock_tokens
        
    def tearDown(self):
        self.patcher.stop()
        
    def test_post_success(self):
        """Test successful token refresh"""
        # Make the request
        response = self.client.post(
            self.url, 
            {'refresh': 'valid_refresh_token'}, 
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.mock_tokens)
        
        # Verify auth_service was called
        self.mock_auth_service.refresh_token.assert_called_once_with('valid_refresh_token')
        
    def test_post_missing_token(self):
        """Test token refresh with missing refresh token"""
        # Make the request without a token
        response = self.client.post(self.url, {}, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.data)
        
    def test_post_auth_failed(self):
        """Test token refresh with AuthenticationFailed"""
        # Set up mock to raise AuthenticationFailed
        self.mock_auth_service.refresh_token.side_effect = AuthenticationFailed('Invalid token')
        
        # Make the request
        response = self.client.post(
            self.url, 
            {'refresh': 'invalid_token'}, 
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        
    def test_post_unexpected_error(self):
        """Test token refresh with unexpected error"""
        # Set up mock to raise Exception
        self.mock_auth_service.refresh_token.side_effect = Exception('Unexpected error')
        
        # Make the request
        response = self.client.post(
            self.url, 
            {'refresh': 'invalid_token'}, 
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('detail', response.data)


class TestLogoutView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('authentication:logout')
        
        # Create a user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Set up mocks
        self.patcher = patch('authentication.views.auth_service')
        self.mock_auth_service = self.patcher.start()
        
        # Mock auth_service.logout
        self.mock_auth_service.logout.return_value = True
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def tearDown(self):
        self.patcher.stop()
        
    def test_post_success(self):
        """Test successful logout"""
        # Make the request
        response = self.client.post(
            self.url, 
            {'refresh': 'valid_refresh_token'}, 
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        
        # Verify auth_service was called
        self.mock_auth_service.logout.assert_called_once_with('valid_refresh_token')
        
    def test_post_missing_token(self):
        """Test logout with missing refresh token"""
        # Make the request without a token
        response = self.client.post(self.url, {}, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.data)
        
    def test_post_logout_failed(self):
        """Test logout with failure from service"""
        # Set up mock to return False
        self.mock_auth_service.logout.return_value = False
        
        # Make the request
        response = self.client.post(
            self.url, 
            {'refresh': 'invalid_token'}, 
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        
    def test_post_unauthorized(self):
        """Test logout when not authenticated"""
        # Unauthenticate the client
        self.client.force_authenticate(user=None)
        
        # Make the request
        response = self.client.post(
            self.url, 
            {'refresh': 'valid_refresh_token'}, 
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUserProfileView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('authentication:user_profile')
        
        # Create a user
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            npm='2206081534',
            angkatan='22',
            role='user'
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_get_success(self):
        """Test successful profile retrieval"""
        # Make the request
        response = self.client.get(self.url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)
        self.assertEqual(response.data['npm'], self.user.npm)
        self.assertEqual(response.data['angkatan'], self.user.angkatan)
        self.assertEqual(response.data['role'], self.user.role)
        
    def test_get_unauthorized(self):
        """Test profile retrieval when not authenticated"""
        # Unauthenticate the client
        self.client.force_authenticate(user=None)
        
        # Make the request
        response = self.client.get(self.url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)