import unittest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
import uuid

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.blacklist.models import Blacklist
from apps.blacklist.services import BlacklistService
from apps.blacklist.views import (
    BlacklistCheckView, CurrentUserBlacklistCheckView,
    BlacklistAddView, BlacklistRemoveView,
    BlacklistHistoryView, ActiveBlacklistsView
)

User = get_user_model()

class TestBlacklistViews(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.npm = '2206081534'
        
        # Create a blacklist
        self.blacklist = Blacklist.objects.create(
            npm=self.npm,
            startDate=self.today,
            endDate=self.tomorrow,
            keterangan='Test reason'
        )
        
        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123',
            role='user',
            npm=self.npm  # Same NPM as blacklist
        )
        
        # Register view URLs - use the same URL names as in your urls.py
        self.urls = {
            'blacklist_check': reverse('blacklist_check'),
            'blacklist_check_me': reverse('blacklist_check_me'),
            'blacklist_add': reverse('blacklist_add'),
            'blacklist_remove': reverse('blacklist_remove'),
            'blacklist_history': reverse('blacklist_history'),
            'active_blacklists': reverse('active_blacklists')
        }
        
    def test_blacklist_check_view(self):
        """Test BlacklistCheckView"""
        url = f"{self.urls['blacklist_check']}?npm={self.npm}"
        
        # No authentication needed for this view
        self.client.force_authenticate(user=self.admin_user)  # Authenticate to pass any permission checks
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['npm'], self.npm)
        self.assertTrue(response.data['is_blacklisted'])
        self.assertIsNotNone(response.data['blacklist_info'])
        
    def test_blacklist_check_view_missing_npm(self):
        """Test BlacklistCheckView with missing NPM"""
        url = self.urls['blacklist_check']
        
        # May need authentication
        self.client.force_authenticate(user=self.admin_user)  # Authenticate to pass any permission checks
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_current_user_blacklist_check_view(self):
        """Test CurrentUserBlacklistCheckView"""
        url = self.urls['blacklist_check_me']
        
        # Authenticate as the blacklisted user
        self.client.force_authenticate(user=self.regular_user)
        
        # Make the request
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['npm'], self.npm)
        self.assertTrue(response.data['is_blacklisted'])
        
    def test_current_user_blacklist_check_view_no_npm(self):
        """Test CurrentUserBlacklistCheckView with user without NPM"""
        url = self.urls['blacklist_check_me']
        
        # Create user without NPM
        user_no_npm = User.objects.create_user(
            email='nonpm@example.com',
            password='password123'
        )
        
        # Authenticate as user without NPM
        self.client.force_authenticate(user=user_no_npm)
        
        # Make the request
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['npm'])
        self.assertFalse(response.data['is_blacklisted'])
        
    def test_blacklist_add_view_success(self):
        """Test BlacklistAddView success"""
        url = self.urls['blacklist_add']
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Prepare data
        data = {
            'npm': '9999999999',
            'reason': 'New reason',
            'end_date': (self.today + timedelta(days=7)).isoformat()
        }
        
        # Make the request
        response = self.client.post(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('blacklist_id', response.data)
        
        # Verify blacklist was created
        self.assertTrue(Blacklist.objects.filter(npm='9999999999').exists())
        
    def test_blacklist_add_view_invalid_data(self):
        """Test BlacklistAddView with invalid data"""
        url = self.urls['blacklist_add']
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Prepare invalid data (missing reason)
        data = {
            'npm': '9999999999',
            'end_date': (self.today + timedelta(days=7)).isoformat()
        }
        
        # Make the request
        response = self.client.post(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('reason', response.data)
        
    def test_blacklist_add_view_unauthorized(self):
        """Test BlacklistAddView with non-admin user"""
        url = self.urls['blacklist_add']
        
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Prepare data
        data = {
            'npm': '9999999999',
            'reason': 'New reason',
            'end_date': (self.today + timedelta(days=7)).isoformat()
        }
        
        # Make the request
        response = self.client.post(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    @patch('apps.blacklist.views.BlacklistService.add_to_blacklist')
    def test_blacklist_add_view_service_error(self, mock_add_to_blacklist):
        """Test BlacklistAddView with service error"""
        url = self.urls['blacklist_add']
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Mock service to raise exception
        mock_add_to_blacklist.side_effect = Exception("Service error")
        
        # Prepare data
        data = {
            'npm': '9999999999',
            'reason': 'New reason',
            'end_date': (self.today + timedelta(days=7)).isoformat()
        }
        
        # Make the request
        response = self.client.post(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('success', response.data)
        self.assertFalse(response.data['success'])
        
    def test_blacklist_remove_view_success(self):
        """Test BlacklistRemoveView success"""
        url = self.urls['blacklist_remove']
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Prepare data
        data = {'npm': self.npm}
        
        # Make the request
        response = self.client.delete(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify blacklist was removed
        self.assertFalse(Blacklist.objects.filter(npm=self.npm).exists())
        
    def test_blacklist_remove_view_not_found(self):
        """Test BlacklistRemoveView with non-existent blacklist"""
        url = self.urls['blacklist_remove']
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Prepare data with non-existent NPM
        data = {'npm': '9999999999'}
        
        # Make the request
        response = self.client.delete(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        
    def test_blacklist_remove_view_invalid_data(self):
        """Test BlacklistRemoveView with invalid data"""
        url = self.urls['blacklist_remove']
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Prepare invalid data (missing npm)
        data = {}
        
        # Make the request
        response = self.client.delete(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('npm', response.data)
        
    def test_blacklist_remove_view_unauthorized(self):
        """Test BlacklistRemoveView with non-admin user"""
        url = self.urls['blacklist_remove']
        
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Prepare data
        data = {'npm': self.npm}
        
        # Make the request
        response = self.client.delete(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    @patch('apps.blacklist.views.BlacklistService.remove_from_blacklist')
    def test_blacklist_remove_view_service_error(self, mock_remove_from_blacklist):
        """Test BlacklistRemoveView with service error"""
        url = self.urls['blacklist_remove']
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Mock service to raise exception
        mock_remove_from_blacklist.side_effect = Exception("Service error")
        
        # Prepare data
        data = {'npm': self.npm}
        
        # Make the request
        response = self.client.delete(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('success', response.data)
        self.assertFalse(response.data['success'])
        
    def test_blacklist_history_view(self):
        """Test BlacklistHistoryView"""
        url = f"{self.urls['blacklist_history']}?npm={self.npm}"
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make the request
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['npm'], self.npm)
        
    def test_blacklist_history_view_missing_npm(self):
        """Test BlacklistHistoryView with missing NPM"""
        url = self.urls['blacklist_history']
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make the request without NPM
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_blacklist_history_view_unauthorized(self):
        """Test BlacklistHistoryView with non-admin user"""
        url = f"{self.urls['blacklist_history']}?npm={self.npm}"
        
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Make the request
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_active_blacklists_view(self):
        """Test ActiveBlacklistsView"""
        url = self.urls['active_blacklists']
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make the request
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['npm'], self.npm)
        
    def test_active_blacklists_view_unauthorized(self):
        """Test ActiveBlacklistsView with non-admin user"""
        url = self.urls['active_blacklists']
        
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Make the request
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)