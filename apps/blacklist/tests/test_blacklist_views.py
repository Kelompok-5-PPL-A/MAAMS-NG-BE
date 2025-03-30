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
from apps.blacklist.serializers import (
    BlacklistInfoSerializer, BlacklistResponseSerializer,
    BlacklistCreateSerializer, BlacklistRemoveSerializer,
    BlacklistHistorySerializer, BlacklistSerializer
)

User = get_user_model()

class TestBlacklistSerializers(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        
        # Create a blacklist
        self.blacklist = Blacklist.objects.create(
            npm='2206081534',
            startDate=self.today,
            endDate=self.tomorrow,
            keterangan='Test reason'
        )
        
    def test_blacklist_info_serializer(self):
        """Test BlacklistInfoSerializer"""
        serializer = BlacklistInfoSerializer(self.blacklist)
        data = serializer.data
        
        self.assertEqual(data['start_date'], self.today.isoformat())
        self.assertEqual(data['end_date'], self.tomorrow.isoformat())
        self.assertEqual(data['reason'], 'Test reason')
        self.assertEqual(data['days_remaining'], (self.tomorrow - self.today).days)
        
    def test_blacklist_response_serializer(self):
        """Test BlacklistResponseSerializer"""
        data = {
            'npm': '2206081534',
            'is_blacklisted': True,
            'blacklist_info': {
                'start_date': self.today.isoformat(),
                'end_date': self.tomorrow.isoformat(),
                'reason': 'Test reason',
                'days_remaining': 1
            },
            'message': 'User is blacklisted'
        }
        
        serializer = BlacklistResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
    def test_blacklist_response_serializer_format_response(self):
        """Test BlacklistResponseSerializer.format_response"""
        # With blacklist
        result = BlacklistResponseSerializer.format_response('2206081534', self.blacklist)
        
        self.assertEqual(result['npm'], '2206081534')
        self.assertTrue(result['is_blacklisted'])
        self.assertIsNotNone(result['blacklist_info'])
        
        # Without blacklist
        result = BlacklistResponseSerializer.format_response('9999999999', None)
        
        self.assertEqual(result['npm'], '9999999999')
        self.assertFalse(result['is_blacklisted'])
        self.assertIsNone(result['blacklist_info'])
        
    def test_blacklist_create_serializer_valid(self):
        """Test BlacklistCreateSerializer with valid data"""
        data = {
            'npm': '9999999999',
            'reason': 'New reason',
            'end_date': (self.today + timedelta(days=7)).isoformat()
        }
        
        serializer = BlacklistCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
    def test_blacklist_create_serializer_invalid(self):
        """Test BlacklistCreateSerializer with invalid data"""
        # Test with end_date in the past
        data = {
            'npm': '9999999999',
            'reason': 'New reason',
            'end_date': (self.today - timedelta(days=1)).isoformat()
        }
        
        serializer = BlacklistCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('End date must be in the future', str(serializer.errors))
        
        # Test with missing fields
        for field in ['npm', 'reason', 'end_date']:
            data = {
                'npm': '9999999999',
                'reason': 'New reason',
                'end_date': (self.today + timedelta(days=7)).isoformat()
            }
            data.pop(field)
            
            serializer = BlacklistCreateSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)
            
    def test_blacklist_remove_serializer(self):
        """Test BlacklistRemoveSerializer"""
        # Valid data
        data = {'npm': '2206081534'}
        serializer = BlacklistRemoveSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Missing NPM
        data = {}
        serializer = BlacklistRemoveSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('npm', serializer.errors)
        
    def test_blacklist_history_serializer(self):
        """Test BlacklistHistorySerializer"""
        data = {
            'id': str(uuid.uuid4()),
            'npm': '2206081534',
            'reason': 'Test reason',
            'start_date': self.today.isoformat(),
            'end_date': self.tomorrow.isoformat(),
            'is_active': True,
            'days_remaining': 1
        }
        
        serializer = BlacklistHistorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
    def test_blacklist_serializer(self):
        """Test BlacklistSerializer"""
        serializer = BlacklistSerializer(self.blacklist)
        data = serializer.data
        
        self.assertEqual(data['npm'], self.blacklist.npm)
        self.assertEqual(data['startDate'], self.today.isoformat())
        self.assertEqual(data['endDate'], self.tomorrow.isoformat())
        self.assertEqual(data['keterangan'], self.blacklist.keterangan)
        self.assertTrue(data['is_active'])
        self.assertEqual(data['days_remaining'], (self.tomorrow - self.today).days)
        
    def test_blacklist_serializer_validation(self):
        """Test BlacklistSerializer validation"""
        # Valid data
        data = {
            'npm': '9999999999',
            'startDate': self.today.isoformat(),
            'endDate': self.tomorrow.isoformat(),
            'keterangan': 'New reason'
        }
        
        serializer = BlacklistSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Invalid end date
        data = {
            'npm': '9999999999',
            'startDate': self.tomorrow.isoformat(),
            'endDate': self.today.isoformat(),  # Before start date
            'keterangan': 'New reason'
        }
        
        serializer = BlacklistSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('End date cannot be before start date', str(serializer.errors))


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
            role='pengguna',
            npm=self.npm  # Same NPM as blacklist
        )
        
    def test_blacklist_check_view(self):
        """Test BlacklistCheckView"""
        url = reverse('blacklist_check') + f'?npm={self.npm}'
        
        # Make the request
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['npm'], self.npm)
        self.assertTrue(response.data['is_blacklisted'])
        self.assertIsNotNone(response.data['blacklist_info'])
        
    def test_blacklist_check_view_missing_npm(self):
        """Test BlacklistCheckView with missing NPM"""
        url = reverse('blacklist_check')
        
        # Make the request without NPM
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_current_user_blacklist_check_view(self):
        """Test CurrentUserBlacklistCheckView"""
        url = reverse('blacklist_check_me')
        
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
        url = reverse('blacklist_check_me')
        
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
        url = reverse('blacklist_add')
        
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
        url = reverse('blacklist_add')
        
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
        url = reverse('blacklist_add')
        
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
        url = reverse('blacklist_add')
        
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
        url = reverse('blacklist_remove')
        
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
        url = reverse('blacklist_remove')
        
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
        url = reverse('blacklist_remove')
        
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
        url = reverse('blacklist_remove')
        
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
        url = reverse('blacklist_remove')
        
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
        url = reverse('blacklist_history') + f'?npm={self.npm}'
        
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
        url = reverse('blacklist_history')
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make the request without NPM
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_blacklist_history_view_unauthorized(self):
        """Test BlacklistHistoryView with non-admin user"""
        url = reverse('blacklist_history') + f'?npm={self.npm}'
        
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Make the request
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_active_blacklists_view(self):
        """Test ActiveBlacklistsView"""
        url = reverse('active_blacklists')
        
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
        url = reverse('active_blacklists')
        
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Make the request
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)