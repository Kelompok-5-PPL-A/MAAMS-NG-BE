import unittest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
import uuid

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.blacklist.models import Blacklist
from apps.blacklist.services import BlacklistService
from apps.blacklist.serializers import BlacklistResponseSerializer

class TestBlacklistService(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)
        
        # Valid blacklist data
        self.npm = '2206081534'
        self.reason = 'Test reason'
        
        # Create a test blacklist
        self.blacklist = Blacklist.objects.create(
            npm=self.npm,
            startDate=self.today,
            endDate=self.tomorrow,
            keterangan=self.reason
        )
        
    def test_check_blacklist_status_blacklisted(self):
        """Test check_blacklist_status with a blacklisted user"""
        # Test the service
        result = BlacklistService.check_blacklist_status(self.npm)
        
        # Verify the result
        self.assertTrue(result['is_blacklisted'])
        self.assertEqual(result['npm'], self.npm)
        self.assertIsNotNone(result['blacklist_info'])
        self.assertEqual(result['blacklist_info']['reason'], self.reason)
        
    def test_check_blacklist_status_not_blacklisted(self):
        """Test check_blacklist_status with a non-blacklisted user"""
        # Test the service with a non-existent NPM
        result = BlacklistService.check_blacklist_status('9999999999')
        
        # Verify the result
        self.assertFalse(result['is_blacklisted'])
        self.assertEqual(result['npm'], '9999999999')
        self.assertIsNone(result['blacklist_info'])
        
    def test_check_blacklist_status_empty_npm(self):
        """Test check_blacklist_status with an empty NPM"""
        # Test the service with an empty NPM
        result = BlacklistService.check_blacklist_status('')
        
        # Verify the result
        self.assertFalse(result['is_blacklisted'])
        self.assertIsNone(result['npm'])
        self.assertIsNone(result['blacklist_info'])
        self.assertIn('No NPM provided', result['message'])
        
    @patch('apps.blacklist.services.BlacklistResponseSerializer')
    def test_check_blacklist_status_uses_serializer(self, mock_serializer):
        """Test check_blacklist_status uses the serializer"""
        # Mock the serializer
        mock_format_response = MagicMock()
        mock_format_response.return_value = {
            'npm': self.npm,
            'is_blacklisted': True,
            'blacklist_info': {'reason': self.reason}
        }
        mock_serializer.format_response = mock_format_response
        
        # Test the service
        BlacklistService.check_blacklist_status(self.npm)
        
        # Verify the serializer was called
        mock_format_response.assert_called_once_with(self.npm, self.blacklist)
        
    def test_add_to_blacklist_success(self):
        """Test add_to_blacklist with valid data"""
        # Test the service
        end_date = self.today + timedelta(days=7)
        npm = '9999999999'  # Different NPM to avoid conflict
        
        result = BlacklistService.add_to_blacklist(npm, "New reason", end_date)
        
        # Verify the result
        self.assertTrue(result['success'])
        self.assertIn('blacklist_id', result)
        
        # Verify the blacklist was created
        blacklist = Blacklist.objects.get(npm=npm)
        self.assertEqual(blacklist.keterangan, "New reason")
        self.assertEqual(blacklist.endDate, end_date)
        
    def test_add_to_blacklist_missing_data(self):
        """Test add_to_blacklist with missing data"""
        # Test with missing npm
        with self.assertRaises(DRFValidationError):
            BlacklistService.add_to_blacklist('', "Reason", self.tomorrow)
            
        # Test with missing reason
        with self.assertRaises(DRFValidationError):
            BlacklistService.add_to_blacklist('9999999999', "", self.tomorrow)
            
        # Test with missing end date
        with self.assertRaises(DRFValidationError):
            BlacklistService.add_to_blacklist('9999999999', "Reason", None)
            
    @patch('apps.blacklist.services.Blacklist')
    def test_add_to_blacklist_validation_error(self, mock_blacklist_class):
        """Test add_to_blacklist with validation error"""
        # Mock Blacklist class to raise ValidationError
        mock_instance = MagicMock()
        mock_instance.full_clean.side_effect = ValidationError("Validation error")
        mock_blacklist_class.return_value = mock_instance
        
        # Test the service
        with self.assertRaises(DRFValidationError):
            BlacklistService.add_to_blacklist('9999999999', "Reason", self.tomorrow)
            
    @patch('apps.blacklist.services.Blacklist')
    def test_add_to_blacklist_other_exception(self, mock_blacklist_class):
        """Test add_to_blacklist with other exception"""
        # Mock Blacklist class to raise Exception
        mock_instance = MagicMock()
        mock_instance.full_clean.side_effect = Exception("Other error")
        mock_blacklist_class.return_value = mock_instance
        
        # Test the service
        with self.assertRaises(DRFValidationError):
            BlacklistService.add_to_blacklist('9999999999', "Reason", self.tomorrow)
            
    def test_remove_from_blacklist_success(self):
        """Test remove_from_blacklist with valid NPM"""
        # Test the service
        result = BlacklistService.remove_from_blacklist(self.npm)
        
        # Verify the result
        self.assertTrue(result['success'])
        
        # Verify the blacklist was deleted
        self.assertEqual(Blacklist.objects.filter(npm=self.npm).count(), 0)
        
    def test_remove_from_blacklist_not_found(self):
        """Test remove_from_blacklist with non-existent NPM"""
        # Test the service with a non-existent NPM
        result = BlacklistService.remove_from_blacklist('9999999999')
        
        # Verify the result
        self.assertFalse(result['success'])
        self.assertIn('No active blacklist found', result['message'])
        
    def test_remove_from_blacklist_missing_npm(self):
        """Test remove_from_blacklist with missing NPM"""
        # Test with empty npm
        with self.assertRaises(DRFValidationError):
            BlacklistService.remove_from_blacklist('')
            
    @patch('apps.blacklist.services.Blacklist.objects.filter')
    def test_remove_from_blacklist_exception(self, mock_filter):
        """Test remove_from_blacklist with exception"""
        # Mock filter to raise Exception
        mock_filter.side_effect = Exception("Filter error")
        
        # Test the service
        with self.assertRaises(DRFValidationError):
            BlacklistService.remove_from_blacklist(self.npm)
            
    def test_get_all_active_blacklists(self):
        """Test get_all_active_blacklists"""
        # Create another blacklist
        Blacklist.objects.create(
            npm='9999999999',
            startDate=self.today,
            endDate=self.tomorrow,
            keterangan='Another reason'
        )
        
        # Test the service
        result = BlacklistService.get_all_active_blacklists()
        
        # Verify the result
        self.assertEqual(len(result), 2)
        
        # Verify the structure of each item
        for item in result:
            self.assertIn('npm', item)
            self.assertIn('reason', item)
            self.assertIn('start_date', item)
            self.assertIn('end_date', item)
            self.assertIn('days_remaining', item)
            
    def test_get_all_active_blacklists_empty(self):
        """Test get_all_active_blacklists with no active blacklists"""
        # Delete all blacklists
        Blacklist.objects.all().delete()
        
        # Test the service
        result = BlacklistService.get_all_active_blacklists()
        
        # Verify the result
        self.assertEqual(len(result), 0)
    
    def test_validation_error_from_model(self):
            """Test handling of ValidationError from model validation"""
            self.today = timezone.now().date()
            self.tomorrow = self.today + timedelta(days=1)
            self.yesterday = self.today - timedelta(days=1)
            
            self.valid_data = {
                'npm': '1234567890',
                'reason': 'Test blacklisting reason',
                'end_date': self.yesterday  # Past date will trigger validation error
            }
            
            with self.assertRaises(DRFValidationError) as context:
                BlacklistService.add_to_blacklist(
                    npm=self.valid_data['npm'],
                    reason=self.valid_data['reason'],
                    end_date=self.valid_data['end_date']
                )
            
            # The error should be wrapped in a DRF ValidationError with our custom message
            self.assertIn("Failed to add student to blacklist", str(context.exception))
            self.assertIn("End date cannot be before start date", str(context.exception))
        
    # def test_get_blacklist_history(self):
    #     """Test get_blacklist_history"""
    #     # Create a past blacklist for the same NPM
    #     Blacklist.objects.create(
    #         npm=self.npm,
    #         startDate=self.yesterday - timedelta(days=10),
    #         endDate=self.yesterday,
    #         keterangan='Past reason'
    #     )
        
    #     # Test the service
    #     result = BlacklistService.get_blacklist_history(self.npm)
        
    #     # Verify the result
    #     self.assertEqual(len(result), 2)
        
    #     # Verify the structure of each item
    #     for item in result:
    #         self.assertEqual(item['npm'], self.npm)
    #         self.assertIn('reason', item)
    #         self.assertIn('start_date', item)
    #         self.assertIn('end_date', item)
    #         self.assertIn('is_active', item)
    #         self.assertIn('days_remaining', item)
            
    # def test_get_blacklist_history_empty(self):
    #     """Test get_blacklist_history with no history"""
    #     # Test the service with a non-existent NPM
    #     result = BlacklistService.get_blacklist_history('9999999999')
        
    #     # Verify the result
    #     self.assertEqual(len(result), 0)
        
    # def test_get_blacklist_history_empty_npm(self):
    #     """Test get_blacklist_history with empty NPM"""
    #     # Test with empty npm
    #     result = BlacklistService.get_blacklist_history('')
        
    #     # Verify the result
    #     self.assertEqual(len(result), 0)