from django.test import TestCase
from authentication.models import CustomUser
from authentication.serializers import (
    CustomUserSerializer, GoogleAuthRequestSerializer, 
    AuthTokenSerializer, LoginResponseSerializer
)

class CustomUserSerializerTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'given_name': 'Test',
            'family_name': 'User',
            'is_active': True,
            'is_staff': False
        }
        self.user = CustomUser.objects.create_user(
            email=self.user_data['email'],
            given_name=self.user_data['given_name'],
            family_name=self.user_data['family_name']
        )
        self.serializer = CustomUserSerializer(instance=self.user)
    
    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(), 
            ['uuid', 'email', 'given_name', 'family_name', 'date_joined', 'is_active', 'is_staff']
        )
    
    def test_field_content(self):
        """Test the content of the serialized fields."""
        data = self.serializer.data
        self.assertEqual(data['email'], self.user_data['email'])
        self.assertEqual(data['given_name'], self.user_data['given_name'])
        self.assertEqual(data['family_name'], self.user_data['family_name'])
        self.assertEqual(data['is_active'], self.user_data['is_active'])
        self.assertEqual(data['is_staff'], self.user_data['is_staff'])


class GoogleAuthRequestSerializerTests(TestCase):
    def test_valid_data(self):
        """Test serializer with valid data."""
        serializer = GoogleAuthRequestSerializer(data={'id_token': 'valid_token'})
        self.assertTrue(serializer.is_valid())
    
    def test_missing_id_token(self):
        """Test serializer with missing id_token."""
        serializer = GoogleAuthRequestSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('id_token', serializer.errors)


class AuthTokenSerializerTests(TestCase):
    def test_serializer_with_data(self):
        """Test serializer with valid token data."""
        token_data = {
            'access_token': 'access_token_value',
            'refresh_token': 'refresh_token_value'
        }
        serializer = AuthTokenSerializer(data=token_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['access_token'], token_data['access_token'])
        self.assertEqual(serializer.data['refresh_token'], token_data['refresh_token'])


class LoginResponseSerializerTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            given_name='Test',
            family_name='User'
        )
        self.user_serializer = CustomUserSerializer(instance=self.user)
        
        self.response_data = {
            'access_token': 'access_token_value',
            'refresh_token': 'refresh_token_value',
            'data': self.user_serializer.data,
            'detail': 'Successfully logged in.'
        }
    
    def test_serializer_with_data(self):
        """Test serializer with valid response data."""
        serializer = LoginResponseSerializer(data=self.response_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['access_token'], self.response_data['access_token'])
        self.assertEqual(serializer.data['refresh_token'], self.response_data['refresh_token'])
        self.assertEqual(serializer.data['detail'], self.response_data['detail'])