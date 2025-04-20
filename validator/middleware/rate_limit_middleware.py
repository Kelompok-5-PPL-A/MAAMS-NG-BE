from django.core.cache import cache
from django.http import JsonResponse
from validator.constants import ErrorMsg

class RateLimitMiddleware:
    """Middleware to handle rate limiting for API requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate = 6  # Number of allowed requests
        self.per = 60  # Time period in seconds
        self.cache = cache
    
    def __call__(self, request):
        # Skip rate limiting for specific paths
        if self._should_skip_rate_limiting(request):
            return self.get_response(request)
        
        identifier = self._get_identifier(request)
        
        # Check if user is allowed
        if not self._is_allowed(identifier):
            return JsonResponse(
                {'error': ErrorMsg.RATE_LIMIT_EXCEEDED},
                status=429
            )
            
        # Process request normally
        return self.get_response(request)
    
    def _should_skip_rate_limiting(self, request):
        """Check if the request should bypass rate limiting"""
        # Skip non-API routes, admin, etc.
        skip_prefixes = ['/admin/', '/static/']
        path = request.path
        
        return any(path.startswith(prefix) for prefix in skip_prefixes)
    
    def _get_identifier(self, request):
        """Get unique identifier for the requester"""
        if request.user.is_authenticated:
            return f"user:{request.user.id}"
        else:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            return f"guest:{ip}"
    
    def _is_allowed(self, identifier):
        """Check if identifier is allowed to make a request"""
        key = f"ratelimit:{identifier}"
        
        # Get current count or create if not exists
        count = self.cache.get(key, 0)
        
        if count >= self.rate:
            # Still increment the counter for tracking purposes
            self.cache.set(key, count + 1, self.per)
            return False
        
        count += 1
        self.cache.set(key, count, self.per)
        
        return True