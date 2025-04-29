import time
import json
from django.test import TestCase, RequestFactory, override_settings
from django.core.cache import cache
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch, Mock
from validator.middleware.rate_limit_middleware import RateLimitMiddleware
from validator.constants import ErrorMsg

@override_settings(RATE_LIMIT={
    'DEFAULT': {
        'RATE': 3,  # Use a lower rate for faster testing
        'PER': 2,   # Use a shorter time period for faster testing
    },
    'CUSTOM_RATES': {
        '/cause/validate/': {
            'RATE': 2,  # Stricter limit for validation
            'PER': 2,
        },
    },
    'EXEMPT_PATHS': ['/admin/', '/static/'],
    'RATE_LIMIT_ALL_PATHS': False,  # Only limit paths in CUSTOM_RATES
})

class RateLimitMiddlewareTest(TestCase):
    def setUp(self):
        # Clear cache before each test
        cache.clear()
        # Create request factory
        self.factory = RequestFactory()
        # Create a mock response function
        self.get_response_mock = Mock(return_value=JsonResponse({"status": "success"}))
        # Create middleware with our mock
        self.middleware = RateLimitMiddleware(self.get_response_mock)
        # Test user identifier
        self.test_user_id = 123
    
    def tearDown(self):
        # Clear cache after each test
        cache.clear()
    
    def _create_authenticated_request(self, path="/api/test/"):
        """Create a request with authenticated user"""
        request = self.factory.get(path)
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.id = self.test_user_id
        return request
    
    def _create_anonymous_request(self, path="/api/test/", ip="127.0.0.1"):
        """Create a request with anonymous user"""
        request = self.factory.get(path)
        request.user = AnonymousUser()
        request.META = {'REMOTE_ADDR': ip}
        return request

    def _get_cache_key(self, path, user_id=None):
        """Helper method to generate the correct cache key"""
        # Extract the path component as done in middleware
        if '/cause/validate/' in path:
            path_component = '/cause/validate/'
        else:
            path_component = path.split('/')[1] if len(path.split('/')) > 1 else path
        
        identifier = f"user:{user_id}" if user_id else "guest:127.0.0.1"
        return f"ratelimit:{path_component}:{identifier}"

    def test_non_rate_limited_path_always_allowed(self):
        """Test that non-rate-limited paths are always allowed"""
        # This path is not in CUSTOM_RATES and should never be rate limited
        request = self._create_authenticated_request(path="/api/v1/auth/login/")
        
        # Even with many requests, it should never be rate limited
        for i in range(10):  # Much more than the limit
            response = self.middleware(request)
            self.assertEqual(response.status_code, 200)
            
        # Verify no counter was set for this path
        key = self._get_cache_key("/api/v1/auth/login/", self.test_user_id)
        self.assertIsNone(cache.get(key))
    
    def test_rate_limited_path_respects_limit(self):
        """Test that rate-limited paths enforce their limits"""
        # Create a test UUID for validation path
        test_uuid = "12345678-1234-5678-1234-567812345678"  
        path = f"/cause/validate/{test_uuid}/"
        request = self._create_authenticated_request(path=path)
        
        # First 2 requests should be allowed (rate=2 for this path)
        for i in range(2):
            response = self.middleware(request)
            self.assertEqual(response.status_code, 200)
        
        # 3rd request should be blocked
        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)
        self.assertIn(ErrorMsg.RATE_LIMIT_EXCEEDED, response.content.decode())
        
        # Verify the counter was set correctly
        key = self._get_cache_key(path, self.test_user_id)
        self.assertEqual(cache.get(key), 3)

    def test_get_rate_limits_for_path(self):
        """Test that _get_rate_limits_for_path returns correct rate limits for paths"""
        # Test with exact path match
        rate, per = self.middleware._get_rate_limits_for_path('/cause/validate/')
        self.assertEqual(rate, 2)  # Custom rate from test settings
        self.assertEqual(per, 2)   # Custom per from test settings
        
        # Test with path that starts with custom path
        rate, per = self.middleware._get_rate_limits_for_path('/cause/validate/12345/')
        self.assertEqual(rate, 2)
        self.assertEqual(per, 2)
        
        # Test with path that has no custom rate (should use defaults)
        rate, per = self.middleware._get_rate_limits_for_path('/api/users/')
        self.assertEqual(rate, 3)  # Default rate from test settings
        self.assertEqual(per, 2)   # Default per from test settings
    
    def test_exempt_paths_never_limited(self):
        """Test that exempt paths are never rate limited"""
        # Admin path is exempt
        path = "/admin/users/"
        request = self._create_authenticated_request(path=path)
        
        # Even with many requests, it should never be rate limited
        for i in range(10):  # Much more than the limit
            response = self.middleware(request)
            self.assertEqual(response.status_code, 200)
            
        # Verify no counter was set for this path
        key = self._get_cache_key(path, self.test_user_id)
        self.assertIsNone(cache.get(key))
    
    def test_rate_limit_reset_after_expiry(self):
        """Test that rate limits reset after the configured time period"""
        # Create a test UUID for validation path
        test_uuid = "12345678-1234-5678-1234-567812345678"
        path = f"/cause/validate/{test_uuid}/"
        request = self._create_authenticated_request(path=path)
        
        # Make requests up to the limit
        for i in range(2):
            response = self.middleware(request)
            self.assertEqual(response.status_code, 200)
        
        # Next request should be blocked
        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)
        
        # Wait for cache expiry (PER=2 seconds in test settings)
        time.sleep(2)
        
        # After expiry, new request should be allowed
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        
        # Counter should be reset to 1
        key = self._get_cache_key(path, self.test_user_id)
        self.assertEqual(cache.get(key), 1)
    
    def test_different_users_have_separate_limits(self):
        """Test that different users have separate rate limits"""
        # Create a test UUID for validation path
        test_uuid = "12345678-1234-5678-1234-567812345678"
        path = f"/cause/validate/{test_uuid}/"
        request1 = self._create_authenticated_request(path=path)
        
        # First user makes requests up to the limit
        for i in range(2):
            response = self.middleware(request1)
            self.assertEqual(response.status_code, 200)
        
        # First user is now blocked
        response1 = self.middleware(request1)
        self.assertEqual(response1.status_code, 429)
        
        # Set up second user
        second_user_id = 456
        request2 = self._create_authenticated_request(path=path)
        request2.user.id = second_user_id
        
        # Second user should still be allowed
        response2 = self.middleware(request2)
        self.assertEqual(response2.status_code, 200)
        
        # Verify separate counters
        key1 = self._get_cache_key(path, self.test_user_id)
        key2 = self._get_cache_key(path, second_user_id)
        self.assertEqual(cache.get(key1), 3)
        self.assertEqual(cache.get(key2), 1)

    def test_extract_ip_address_from_x_forwarded_for(self):
        """Test that IP address is correctly extracted from X-Forwarded-For header"""
        request = self._create_anonymous_request()
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        
        identifier = self.middleware._get_identifier(request)
        self.assertEqual(identifier, 'guest:192.168.1.1')
        
        # Test with single IP
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.2'
        identifier = self.middleware._get_identifier(request)
        self.assertEqual(identifier, 'guest:192.168.1.2')
        
        # Test with spaces
        request.META['HTTP_X_FORWARDED_FOR'] = ' 192.168.1.3 , 10.0.0.1'
        identifier = self.middleware._get_identifier(request)
        self.assertEqual(identifier, 'guest:192.168.1.3')

    def test_get_identifier_with_empty_x_forwarded_for(self):
        """Test that _get_identifier handles empty or None X-Forwarded-For value"""
        request = self._create_anonymous_request(ip='192.168.6.6')
        
        # Test with empty X-Forwarded-For header
        request.META['HTTP_X_FORWARDED_FOR'] = ''
        identifier = self.middleware._get_identifier(request)
        self.assertEqual(identifier, 'guest:192.168.6.6')
        
        # Test with None X-Forwarded-For
        request.META['HTTP_X_FORWARDED_FOR'] = None
        identifier = self.middleware._get_identifier(request)
        self.assertEqual(identifier, 'guest:192.168.6.6')

    def test_get_identifier_fallback_to_remote_addr(self):
        """Test that _get_identifier falls back to REMOTE_ADDR when X-Forwarded-For is not present"""
        # Create request without X-Forwarded-For header
        request = self._create_anonymous_request(ip='192.168.5.5')
        
        # Ensure HTTP_X_FORWARDED_FOR is not in META
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            del request.META['HTTP_X_FORWARDED_FOR']
        
        # Check that the identifier uses REMOTE_ADDR
        identifier = self.middleware._get_identifier(request)
        self.assertEqual(identifier, 'guest:192.168.5.5')
        
        # Test fallback to default IP if REMOTE_ADDR is also missing
        del request.META['REMOTE_ADDR']
        identifier = self.middleware._get_identifier(request)
        self.assertEqual(identifier, 'guest:0.0.0.0')

    def test_is_allowed_counters_and_expiry(self):
        """Test that _is_allowed correctly manages counters and returns expected values"""
        # Create a test key
        test_key = 'ratelimit:test:user:123'
        
        # First requests should be allowed and set counter to 1
        result1 = self.middleware._is_allowed(test_key, 3, 10)
        self.assertTrue(result1)
        self.assertEqual(cache.get(test_key), 1)
        
        # Second request should be allowed and set counter to 2
        result2 = self.middleware._is_allowed(test_key, 3, 10)
        self.assertTrue(result2)
        self.assertEqual(cache.get(test_key), 2)
        
        # Third request should be allowed and set counter to 3
        result3 = self.middleware._is_allowed(test_key, 3, 10)
        self.assertTrue(result3)
        self.assertEqual(cache.get(test_key), 3)
        
        # Fourth request should be denied but still increment the counter to 4
        result4 = self.middleware._is_allowed(test_key, 3, 10)
        self.assertFalse(result4)
        self.assertEqual(cache.get(test_key), 4)
        
        # Fifth request should be denied but still increment the counter to 5
        result5 = self.middleware._is_allowed(test_key, 3, 10)
        self.assertFalse(result5)
        self.assertEqual(cache.get(test_key), 5)
        
        # Test with is_allowed public method - should delegate to _is_allowed
        cache.delete(test_key)  # Reset counter
        
        # First request should be allowed
        result1 = self.middleware.is_allowed(test_key, 2, 10)
        self.assertTrue(result1)
        self.assertEqual(cache.get(test_key), 1)
        
        # Second request should be allowed
        result2 = self.middleware.is_allowed(test_key, 2, 10)
        self.assertTrue(result2)
        self.assertEqual(cache.get(test_key), 2)
        
        # Third request should be denied
        result3 = self.middleware.is_allowed(test_key, 2, 10)
        self.assertFalse(result3)
        self.assertEqual(cache.get(test_key), 3)

    def test_is_allowed_increments_counter_when_over_limit(self):
        """Test that _is_allowed increments the counter even when over the limit"""
        # Create a test key and simulate it being exactly at the limit
        test_key = 'ratelimit:test:over_limit'
        rate = 5
        per = 10
        
        # First set the counter to exactly the rate limit
        cache.set(test_key, rate, per)
        
        # Check that request is denied but counter is still incremented
        result = self.middleware._is_allowed(test_key, rate, per)
        self.assertFalse(result)
        self.assertEqual(cache.get(test_key), rate + 1)
        
        # Make another request, should be denied and counter increased again
        result = self.middleware._is_allowed(test_key, rate, per)
        self.assertFalse(result)
        self.assertEqual(cache.get(test_key), rate + 2)
    
    def test_is_path_in_custom_rates(self):
        """Test that _is_path_in_custom_rates correctly identifies paths in custom rates"""
        # Test with path that exactly matches a custom rate path
        self.assertTrue(self.middleware._is_path_in_custom_rates('/cause/validate/'))
        
        # Test with path that starts with a custom rate path
        self.assertTrue(self.middleware._is_path_in_custom_rates('/cause/validate/12345/'))
        
        # Test with path that doesn't match any custom rate path
        self.assertFalse(self.middleware._is_path_in_custom_rates('/api/v1/users/'))
        
        # Test with partial match that doesn't start with the custom path
        self.assertFalse(self.middleware._is_path_in_custom_rates('/api/cause/validate/'))

    def test_get_identifier_for_authenticated_vs_anonymous_users(self):
        """Test that _get_identifier returns different identifiers for authenticated and anonymous users"""
        # Test with authenticated user
        auth_request = self._create_authenticated_request()
        auth_identifier = self.middleware._get_identifier(auth_request)
        self.assertEqual(auth_identifier, f"user:{self.test_user_id}")
        
        # Test with anonymous user
        anon_ip = "192.168.2.2"
        anon_request = self._create_anonymous_request(ip=anon_ip)
        anon_identifier = self.middleware._get_identifier(anon_request)
        self.assertEqual(anon_identifier, f"guest:{anon_ip}")
        
        # Verify different users get different identifiers
        auth_request2 = self._create_authenticated_request()
        auth_request2.user.id = 456  # Different user ID
        auth_identifier2 = self.middleware._get_identifier(auth_request2)
        self.assertEqual(auth_identifier2, "user:456")
        self.assertNotEqual(auth_identifier, auth_identifier2)
        
        # Verify different IPs get different identifiers
        anon_request2 = self._create_anonymous_request(ip="10.0.0.1")
        anon_identifier2 = self.middleware._get_identifier(anon_request2)
        self.assertEqual(anon_identifier2, "guest:10.0.0.1")
        self.assertNotEqual(anon_identifier, anon_identifier2)