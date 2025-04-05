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

from authentication.views import (
    GoogleLoginView, SSOLoginView, SSOLogoutView,
    TokenRefreshView, LogoutView, UserProfileView
)
from authentication.services.auth_service import AuthenticationService
from authentication.services.jwt_token import JWTTokenService

User = get_user_model()

class TestGoogleLoginView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('authentication:google_login')
        
        # Set up mocks
        self.patcher = patch('authentication.views.auth_service')
        self.mock_auth_service = self.patcher.start()
        
        # Create a real user for serialization
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        
        # Mock auth_service.authenticate_with_provider
        self.mock_tokens = {'access': 'access_token', 'refresh': 'refresh_token'}
        self.mock_auth_service.authenticate_with_provider.return_value = (
            self.mock_tokens, self.user, False
        )
        
    def tearDown(self):
        self.patcher.stop()
        
    def test_post_success(self):
        """Test successful Google login"""
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
        
        # Verify auth_service was called
        self.mock_auth_service.authenticate_with_provider.assert_called_once_with(
            'google', 'valid_token'
        )
        
    def test_post_new_user(self):
        """Test Google login for a new user"""
        # Set up mock to return a new user
        self.mock_auth_service.authenticate_with_provider.return_value = (
            self.mock_tokens, self.user, True
        )
        
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
        
    def test_post_parse_error(self):
        """Test Google login with ParseError"""
        # Set up mock to raise ParseError
        from rest_framework.exceptions import ParseError
        self.mock_auth_service.authenticate_with_provider.side_effect = ParseError('Parse error')
        
        # Make the request
        response = self.client.post(
            self.url, 
            {'id_token': 'invalid_token'}, 
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        
    def test_post_auth_failed(self):
        """Test Google login with AuthenticationFailed"""
        # Set up mock to raise AuthenticationFailed
        from rest_framework.exceptions import AuthenticationFailed
        self.mock_auth_service.authenticate_with_provider.side_effect = AuthenticationFailed('Auth failed')
        
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
        # Set up mock to raise Exception
        self.mock_auth_service.authenticate_with_provider.side_effect = Exception('Unexpected error')
        
        # Make the request
        response = self.client.post(
            self.url, 
            {'id_token': 'invalid_token'}, 
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('detail', response.data)

class TestSSOLoginView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('authentication:sso_login')
        
        # Set up mocks
        self.patcher = patch('authentication.views.auth_service')
        self.mock_auth_service = self.patcher.start()
        
        # Create a real user for serialization
        self.user = User.objects.create_user(
            email='test@ui.ac.id',
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        
        # Mock auth_service.authenticate_with_provider
        self.mock_tokens = {'access': 'access_token', 'refresh': 'refresh_token'}
        self.mock_auth_service.authenticate_with_provider.return_value = (
            self.mock_tokens, self.user, False
        )
        
    def tearDown(self):
        self.patcher.stop()
        
    def test_get_success(self):
        """Test successful SSO login"""
        # Make the request
        response = self.client.get(f"{self.url}?ticket=valid_ticket")
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['access_token'], 'access_token')
        self.assertEqual(response.data['refresh_token'], 'refresh_token')
        self.assertFalse(response.data['is_new_user'])
        
        # Verify auth_service was called
        self.mock_auth_service.authenticate_with_provider.assert_called_once_with(
            'sso', 'valid_ticket'
        )
        
    def test_get_new_user(self):
        """Test SSO login for a new user"""
        # Set up mock to return a new user
        self.mock_auth_service.authenticate_with_provider.return_value = (
            self.mock_tokens, self.user, True
        )
        
        # Make the request
        response = self.client.get(f"{self.url}?ticket=valid_ticket")
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_new_user'])
        self.assertIn('Successfully registered', response.data['detail'])
        
    def test_get_missing_ticket(self):
        """Test SSO login with missing ticket"""
        # Make the request without a ticket
        response = self.client.get(self.url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_get_auth_failed(self):
        """Test SSO login with AuthenticationFailed"""
        # Set up mock to raise AuthenticationFailed
        from rest_framework.exceptions import AuthenticationFailed
        self.mock_auth_service.authenticate_with_provider.side_effect = AuthenticationFailed('Auth failed')
        
        # Make the request
        response = self.client.get(f"{self.url}?ticket=invalid_ticket")
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        
    def test_get_auth_failed_blacklist(self):
        """Test SSO login with blacklisted user"""
        # Set up mock to raise AuthenticationFailed with blacklist_info
        from rest_framework.exceptions import AuthenticationFailed
        error_detail = {
            'error': 'User is blacklisted',
            'blacklist_info': {
                'npm': '2206081534',
                'reason': 'Test reason',
                'blacklisted_at': '2022-01-01',
                'expires_at': '2022-12-31'
            }
        }
        mock_exception = AuthenticationFailed(error_detail)
        mock_exception.detail = error_detail  # Add detail attribute
        self.mock_auth_service.authenticate_with_provider.side_effect = mock_exception
        
        # Make the request
        response = self.client.get(f"{self.url}?ticket=blacklisted_ticket")
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('blacklist_info', response.data)
        
    def test_get_unexpected_error(self):
        """Test SSO login with unexpected error"""
        # Set up mock to raise Exception
        self.mock_auth_service.authenticate_with_provider.side_effect = Exception('Unexpected error')
        
        # Make the request
        response = self.client.get(f"{self.url}?ticket=invalid_ticket")
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        from rest_framework.exceptions import AuthenticationFailed
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