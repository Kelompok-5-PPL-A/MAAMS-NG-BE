import unittest
from unittest.mock import patch
import uuid

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class TestCustomUserManager(TestCase):
    def test_create_user(self):
        """Test creating a regular user"""
        email = 'test@example.com'
        username = email.split('@')[0]
        user = User.objects.create_user(email=email)
        
        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.role, 'user')
        self.assertFalse(user.has_usable_password())
        
    def test_create_user_with_custom_fields(self):
        """Test creating a user with custom fields"""
        email = 'test@example.com'
        username = email.split('@')[0]
        user = User.objects.create_user(
            email=email,
            username=username,
            password='password123',
            first_name='Test',
            last_name='User',
            role='guest'
        )
        
        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, 'guest')
        self.assertTrue(user.check_password('password123'))
        
    def test_create_user_no_email(self):
        """Test creating a user without email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='')
            
    def test_create_superuser(self):
        """Test creating a superuser"""
        email = 'admin@example.com'
        user = User.objects.create_superuser(
            email=email,
            password='adminpass123'
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.check_password('adminpass123'))
        
    def test_create_superuser_invalid_is_staff(self):
        """Test creating a superuser with is_staff=False raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )
            
    def test_create_superuser_invalid_is_superuser(self):
        """Test creating a superuser with is_superuser=False raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )


class TestCustomUser(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            role='user',
            npm='2206081534',
            angkatan='22'
        )
        
    def test_str(self):
        """Test the string representation of the user"""
        self.assertEqual(str(self.user), 'test@example.com')
        
    def test_get_full_name(self):
        """Test the get_full_name method"""
        self.assertEqual(self.user.get_full_name(), 'Test User')
        
        # Test with empty first and last name
        user_no_name = User.objects.create_user(
            email='noname@example.com'
        )
        self.assertEqual(user_no_name.get_full_name(), 'noname@example.com')
        
    def test_get_short_name(self):
        """Test the get_short_name method"""
        self.assertEqual(self.user.get_short_name(), 'Test')
        
        # Test with empty first name
        user_no_name = User.objects.create_user(
            email='noname@example.com'
        )
        self.assertEqual(user_no_name.get_short_name(), 'noname')
        
    def test_is_admin(self):
        """Test the is_admin method"""
        self.assertFalse(self.user.is_admin())
        
        admin_user = User.objects.create_user(
            email='admin@example.com',
            role='admin'
        )
        self.assertTrue(admin_user.is_admin())
        
    def test_has_role(self):
        """Test the has_role method"""
        self.assertTrue(self.user.has_role('user'))
        self.assertFalse(self.user.has_role('admin'))
        
        admin_user = User.objects.create_user(
            email='admin@example.com',
            role='admin'
        )
        self.assertTrue(admin_user.has_role('admin'))
        self.assertFalse(admin_user.has_role('user'))