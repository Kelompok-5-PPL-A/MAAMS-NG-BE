from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from authentication.models import CustomUser, CustomUserManager

class CustomUserManagerTests(TestCase):
    def test_create_user(self):
        """Test creating a user with an email."""
        email = 'test@example.com'
        user = CustomUser.objects.create_user(email=email)

        self.assertEqual(user.email, email)
        self.assertEqual(user.username, email)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.has_usable_password())
    
    def test_create_user_with_password(self):
        """Test creating a user with an email and password."""
        email = 'test@example.com'
        password = 'testpassword'
        user = CustomUser.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
    
    def test_create_user_with_username(self):
        """Test creating a user with a custom username."""
        email = 'test@example.com'
        username = 'testuser'
        user = CustomUser.objects.create_user(email=email, username=username)

        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
    
    def test_create_user_without_email(self):
        """Test creating a user without an email raises an error."""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email='')
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        email = 'admin@example.com'
        password = 'testpassword'
        user = CustomUser.objects.create_superuser(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertEqual(user.username, email)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(password))
    
    def test_create_superuser_with_invalid_flags(self):
        """Test creating a superuser with invalid flags raises errors."""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email='admin@example.com', 
                password='testpassword',
                is_staff=False
            )
        
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email='admin@example.com', 
                password='testpassword',
                is_superuser=False
            )

class CustomUserTests(TestCase):
    def test_create_user(self):
        """Test creating a user directly."""
        user = CustomUser.objects.create(
            email='test@example.com',
            username='testuser'
        )

        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
    
    def test_user_str(self):
        """Test the __str__ method of CustomUser."""
        user = CustomUser.objects.create(
            email='test@example.com',
            username='testuser'
        )

        self.assertEqual(str(user), 'test@example.com')
    
    def test_email_uniqueness(self):
        """Test that users with duplicate emails can't be created."""
        CustomUser.objects.create(
            email='duplicate@example.com',
            username='user1'
        )
        
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                email='duplicate@example.com',
                username='user2'
            )
    
    def test_username_uniqueness(self):
        """Test that users with duplicate usernames can't be created."""
        CustomUser.objects.create(
            email='user1@example.com',
            username='duplicate'
        )
        
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                email='user2@example.com',
                username='duplicate'
            )
    
    def test_google_id_uniqueness(self):
        """Test that users with duplicate Google IDs can't be created."""
        CustomUser.objects.create(
            email='user1@example.com',
            username='user1',
            google_id='123456'
        )
        
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                email='user2@example.com',
                username='user2',
                google_id='123456'
            )