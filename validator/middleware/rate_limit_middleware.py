import logging
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from validator.constants import ErrorMsg

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Middleware to handle rate limiting for API requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Get rate limit settings from settings.py
        rate_limit_config = getattr(settings, 'RATE_LIMIT', {})
        self.default_rate = rate_limit_config.get('DEFAULT', {}).get('RATE', 6)
        self.default_per = rate_limit_config.get('DEFAULT', {}).get('PER', 60)
        self.custom_rates = rate_limit_config.get('CUSTOM_RATES', {})
        self.exempt_paths = rate_limit_config.get('EXEMPT_PATHS', [])
        self.rate_limit_all = rate_limit_config.get('RATE_LIMIT_ALL_PATHS', True)
        
        self.cache = cache
    
    def __call__(self, request):
        # Skip rate limiting for exempt paths
        if self._is_path_exempt(request.path):
            return self.get_response(request)
        
        # Skip if path is not in custom rates and we're not limiting all paths
        if not self.rate_limit_all and not self._is_path_in_custom_rates(request.path):
            return self.get_response(request)
        
        # Get rate limits for this path and create cache key based on path
        rate, per = self._get_rate_limits_for_path(request.path)
        identifier = self._get_identifier(request)
        path_key = self._get_path_specific_key(request.path, identifier)
        
        # Check if user is allowed to make this request
        if not self._is_allowed(path_key, rate, per):
            return JsonResponse(
                {'error': ErrorMsg.RATE_LIMIT_EXCEEDED},
                status=429
            )
        
        # Process request normally
        return self.get_response(request)
    
    def _get_path_specific_key(self, path, identifier):
        """Create a path-specific cache key"""
        matching_prefix = ''
        for prefix in self.custom_rates:
            if path.startswith(prefix) and len(prefix) > len(matching_prefix):
                matching_prefix = prefix
        
        path_component = matching_prefix if matching_prefix else path.split('/')[1]
        key = f"ratelimit:{path_component}:{identifier}"
        logger.debug(f"Cache Key: {key}")
        return key
    
    def _get_rate_limits_for_path(self, path):
        """Get the rate limits for the current path"""
        # Find best matching custom rate (most specific path prefix)
        best_match = None
        best_match_len = 0
        
        for custom_path, limits in self.custom_rates.items():
            if path.startswith(custom_path) and len(custom_path) > best_match_len:
                best_match = limits
                best_match_len = len(custom_path)
        
        if best_match:
            return best_match.get('RATE', self.default_rate), best_match.get('PER', self.default_per)
        else:
            return self.default_rate, self.default_per
    
    def _get_identifier(self, request):
        """Get unique identifier for the requester"""
        if request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
        else:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
            identifier = f"guest:{ip}"
        
        logger.debug(f"Identifier: {identifier}")
        return identifier
    
    def _is_allowed(self, key, rate, per):
        """Check if identifier is allowed to make a request"""
        count = self.cache.get(key, 0)
        logger.debug(f"Current Count: {count}, Rate: {rate}, Per: {per}")
        
        if count >= rate:
            self.cache.set(key, count + 1, per)
            return False
        
        count += 1
        self.cache.set(key, count, per)
        return True
        
    def is_allowed(self, key, rate, per):
        """
        Public method to check if a request is allowed based on rate limits.
        Delegates to the private _is_allowed method.
        """
        return self._is_allowed(key, rate, per)
    
    def _is_path_exempt(self, path):
        """Check if path is exempt from rate limiting"""
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False
    
    def _is_path_in_custom_rates(self, path):
        """Check if path is specified in custom rates"""
        for custom_path in self.custom_rates:
            if path.startswith(custom_path):
                return True
        return False
    