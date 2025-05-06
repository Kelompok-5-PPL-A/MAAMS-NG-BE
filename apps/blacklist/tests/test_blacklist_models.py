import unittest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.blacklist.models import Blacklist

class TestBlacklistModel(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)
        
        # Valid blacklist data
        self.valid_data = {
            'npm': '2206081534',
            'startDate': self.today,
            'endDate': self.tomorrow,
            'keterangan': 'Test reason'
        }
        
    def test_create_blacklist(self):
        """Test creating a valid blacklist entry"""
        blacklist = Blacklist.objects.create(**self.valid_data)
        
        self.assertEqual(blacklist.npm, self.valid_data['npm'])
        self.assertEqual(blacklist.startDate, self.valid_data['startDate'])
        self.assertEqual(blacklist.endDate, self.valid_data['endDate'])
        self.assertEqual(blacklist.keterangan, self.valid_data['keterangan'])
        
    def test_string_representation(self):
        """Test string representation of blacklist"""
        blacklist = Blacklist.objects.create(**self.valid_data)
        expected = f"Blacklist-{self.valid_data['npm']} ({self.valid_data['startDate']} - {self.valid_data['endDate']}), {self.valid_data['keterangan']}"
        
        self.assertEqual(str(blacklist), expected)
        
    def test_clean_valid_dates(self):
        """Test validation with valid dates"""
        blacklist = Blacklist(**self.valid_data)
        # This should not raise ValidationError
        blacklist.clean()
        
    def test_clean_invalid_end_date(self):
        """Test validation with end date before start date"""
        invalid_data = self.valid_data.copy()
        invalid_data['endDate'] = self.yesterday
        
        blacklist = Blacklist(**invalid_data)
        with self.assertRaises(ValidationError):
            blacklist.clean()
            
    def test_clean_missing_fields(self):
        """Test validation with missing required fields"""
        # Test each required field
        required_fields = ['startDate', 'endDate', 'npm', 'keterangan']
        
        for field in required_fields:
            invalid_data = self.valid_data.copy()
            invalid_data[field] = None
            
            blacklist = Blacklist(**invalid_data)
            with self.assertRaises(ValidationError):
                blacklist.clean()
                
    def test_clean_overlapping_blacklists(self):
        """Test validation with overlapping blacklist periods"""
        # Create a blacklist entry
        Blacklist.objects.create(**self.valid_data)
        
        # Create a new entry with overlapping period
        overlapping_data = self.valid_data.copy()
        
        # Start date in the middle of existing period
        overlapping_data['startDate'] = self.today
        
        blacklist = Blacklist(**overlapping_data)
        with self.assertRaises(ValidationError):
            blacklist.clean()
            
    def test_clean_non_overlapping_blacklists(self):
        """Test validation with non-overlapping blacklist periods"""
        # Create a blacklist entry
        Blacklist.objects.create(**self.valid_data)
        
        # Create a new entry with non-overlapping period
        non_overlapping_data = self.valid_data.copy()
        
        # Start date after existing period ends
        future_start = self.tomorrow + timedelta(days=1)
        future_end = future_start + timedelta(days=1)
        non_overlapping_data['startDate'] = future_start
        non_overlapping_data['endDate'] = future_end
        
        blacklist = Blacklist(**non_overlapping_data)
        # This should not raise ValidationError
        blacklist.clean()
        
    def test_clean_update_same_instance(self):
        """Test validation when updating the same instance"""
        # Create a blacklist entry
        blacklist = Blacklist.objects.create(**self.valid_data)
        
        # Update the same instance
        blacklist.keterangan = "Updated reason"
        
        # This should not raise ValidationError
        blacklist.clean()
            
    def test_is_active_property_active(self):
        """Test is_active property with active blacklist"""
        # Create a blacklist with current period
        blacklist = Blacklist.objects.create(**self.valid_data)
        
        self.assertTrue(blacklist.is_active)
        
    def test_is_active_property_inactive_past(self):
        """Test is_active property with past blacklist"""
        # Create a blacklist with past period
        past_data = self.valid_data.copy()
        past_data['startDate'] = self.yesterday - timedelta(days=2)
        past_data['endDate'] = self.yesterday
        
        blacklist = Blacklist.objects.create(**past_data)
        
        self.assertFalse(blacklist.is_active)
        
    def test_is_active_property_inactive_future(self):
        """Test is_active property with future blacklist"""
        # Create a blacklist with future period
        future_data = self.valid_data.copy()
        future_start = self.tomorrow
        future_end = future_start + timedelta(days=1)
        future_data['startDate'] = future_start
        future_data['endDate'] = future_end
        
        blacklist = Blacklist.objects.create(**future_data)
        
        self.assertFalse(blacklist.is_active)
        
    def test_days_remaining_active(self):
        """Test days_remaining property with active blacklist"""
        # Create a blacklist with current period
        blacklist = Blacklist.objects.create(**self.valid_data)
        
        # Expected days remaining
        expected_days = (blacklist.endDate - self.today).days
        
        self.assertEqual(blacklist.days_remaining, expected_days)
        
    def test_days_remaining_expired(self):
        """Test days_remaining property with expired blacklist"""
        # Create a blacklist with past period
        past_data = self.valid_data.copy()
        past_data['startDate'] = self.yesterday - timedelta(days=2)
        past_data['endDate'] = self.yesterday
        
        blacklist = Blacklist.objects.create(**past_data)
        
        self.assertEqual(blacklist.days_remaining, 0)
        
    def test_days_remaining_future(self):
        """Test days_remaining property with future blacklist"""
        # Create a blacklist with future period
        future_data = self.valid_data.copy()
        future_start = self.tomorrow
        future_end = future_start + timedelta(days=5)
        future_data['startDate'] = future_start
        future_data['endDate'] = future_end
        
        blacklist = Blacklist.objects.create(**future_data)
        
        # Expected days remaining (total duration)
        expected_days = (future_end - future_start).days
        
        self.assertEqual(blacklist.days_remaining, expected_days)
        
    def test_is_user_blacklisted_false(self):
        """Test is_user_blacklisted class method with non-blacklisted user"""
        self.assertFalse(Blacklist.is_user_blacklisted('9999999999'))
        
    def test_get_active_blacklist_found(self):
        """Test get_active_blacklist class method with existing blacklist"""
        # Create a blacklist
        blacklist = Blacklist.objects.create(**self.valid_data)
        
        result = Blacklist.get_active_blacklist(self.valid_data['npm'])
        
        self.assertEqual(result, blacklist)
        
    def test_get_active_blacklist_not_found(self):
        """Test get_active_blacklist class method with no blacklist"""
        result = Blacklist.get_active_blacklist('9999999999')
        
        self.assertIsNone(result)

class BlacklistModelSaveTest(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.valid_data = {
            'npm': '1234567890',
            'startDate': self.today,
            'endDate': self.today + timedelta(days=10),
            'keterangan': 'Test blacklist'
        }

    def test_save_valid_blacklist(self):
        # Test that saving a valid blacklist succeeds
        blacklist = Blacklist(**self.valid_data)
        result = blacklist.save()
        
        # Verify the blacklist was saved to the database
        saved_blacklist = Blacklist.objects.get(pk=blacklist.id)
        self.assertEqual(saved_blacklist.npm, self.valid_data['npm'])
        self.assertEqual(saved_blacklist.keterangan, self.valid_data['keterangan'])
    
    def test_save_invalid_dates(self):
        # Test that saving with end date before start date raises ValidationError
        invalid_data = self.valid_data.copy()
        invalid_data['startDate'] = self.today
        invalid_data['endDate'] = self.today - timedelta(days=1)
        
        blacklist = Blacklist(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            blacklist.save()
        
        self.assertIn("End date cannot be before start date", str(context.exception))