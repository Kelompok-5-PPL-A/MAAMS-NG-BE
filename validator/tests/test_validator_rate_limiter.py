from validator.enums import ValidationType
from unittest.mock import patch, Mock
from django.test import TestCase
from django.core.cache import cache
from validator.utils.rate_limiter import RateLimiter
from validator.exceptions import RateLimitExceededException
from validator.services import CausesService
import time

class RateLimiterTest(TestCase):
    def setUp(self):
        # Clear cache before each test
        cache.clear()
        # Create test rate limiter with 3 requests per 2 seconds
        self.rate_limiter = RateLimiter(rate=3, per=2)
        # Test user identifier
        self.test_user = "test_user_123"
    
    def tearDown(self):
        # Clear cache after each test
        cache.clear()
    
    def test_first_request_allowed(self):
        """Test that the first request is always allowed"""
        self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # Verify the counter is set to 1
        key = f"ratelimit:{self.test_user}"
        self.assertEqual(cache.get(key), 1)
    
    def test_under_limit_requests_allowed(self):
        """Test that requests under the limit are allowed"""
        # Make 3 requests (at the limit)
        for i in range(3):
            self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # Verify the counter is set to 3
        key = f"ratelimit:{self.test_user}"
        self.assertEqual(cache.get(key), 3)
    
    def test_over_limit_requests_blocked(self):
        """Test that requests over the limit are blocked"""
        # Make 3 requests (at the limit)
        for i in range(3):
            self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # The 4th request should be blocked
        self.assertFalse(self.rate_limiter.is_allowed(self.test_user))
        
        # Verify the counter is still 4 (it increments even when blocked)
        key = f"ratelimit:{self.test_user}"
        self.assertEqual(cache.get(key), 4)
    
    def test_limit_reset_after_expiry(self):
        """Test that the limit resets after expiry time"""
        # Make 3 requests (at the limit)
        for i in range(3):
            self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # The 4th request should be blocked
        self.assertFalse(self.rate_limiter.is_allowed(self.test_user))
        
        # Wait for cache expiry (use a shorter time for tests)
        time.sleep(2)
        
        # After expiry, new request should be allowed
        self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # Counter should be reset to 1
        key = f"ratelimit:{self.test_user}"
        self.assertEqual(cache.get(key), 1)
    
    def test_different_users_have_separate_limits(self):
        """Test that different users have separate rate limits"""
        # First user makes max requests
        for i in range(3):
            self.assertTrue(self.rate_limiter.is_allowed(self.test_user))
        
        # First user is now blocked
        self.assertFalse(self.rate_limiter.is_allowed(self.test_user))
        
        # Second user should still be allowed
        second_user = "another_test_user"
        self.assertTrue(self.rate_limiter.is_allowed(second_user))
        
        # Verify separate counters
        self.assertEqual(cache.get(f"ratelimit:{self.test_user}"), 4)
        self.assertEqual(cache.get(f"ratelimit:{second_user}"), 1)
    
    def test_custom_rate_limits(self):
        """Test that custom rate limits work correctly"""
        # Create a stricter rate limiter (2 requests per 5 seconds)
        strict_limiter = RateLimiter(rate=2, per=5)
        
        # First 2 requests are allowed
        self.assertTrue(strict_limiter.is_allowed(self.test_user))
        self.assertTrue(strict_limiter.is_allowed(self.test_user))
        
        # Third request is blocked
        self.assertFalse(strict_limiter.is_allowed(self.test_user))
        
        # Regular limiter should still allow 3 requests
        another_user = "yet_another_user"
        self.assertTrue(self.rate_limiter.is_allowed(another_user))
        self.assertTrue(self.rate_limiter.is_allowed(another_user))
        self.assertTrue(self.rate_limiter.is_allowed(another_user))
        self.assertFalse(self.rate_limiter.is_allowed(another_user))

    @patch('validator.services.Groq')
    @patch('validator.utils.rate_limiter.RateLimiter.is_allowed')
    def test_api_call_rate_limit_exceeded(self, mock_is_allowed, mock_groq):
        """Test API call when rate limit is exceeded"""
        # Configure mock to return False for is_allowed (rate limit exceeded)
        mock_is_allowed.return_value = False
        
        service = CausesService()
        system_message = "test system message"
        user_prompt = "test user prompt"
        
        # Test with authenticated user
        mock_authenticated_request = Mock()
        mock_authenticated_request.user = Mock(is_authenticated=True)
        mock_authenticated_request.user.id = 123
        
        # Verify that RateLimitExceededException is raised
        with self.assertRaises(RateLimitExceededException) as context:
            service.api_call(system_message, user_prompt, ValidationType.NORMAL, mock_authenticated_request)
        
        # Check that the rate limiter was called with the correct identifier
        mock_is_allowed.assert_called_with('user:123')
        
        # Verify exception message
        self.assertEqual(str(context.exception), "Rate limit exceeded. Maximum 6 requests per minute allowed.")
        
        # Ensure the Groq client was never called
        mock_groq.assert_not_called()