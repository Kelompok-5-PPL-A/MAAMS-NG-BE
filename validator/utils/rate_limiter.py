from django.core.cache import cache

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, rate=6, per=60):
        self.rate = rate  # Number of allowed requests
        self.per = per    # Time period in seconds
        self.cache = cache  # Using Django's cache framework
    
    def is_allowed(self, user_id):
        """Check if user is allowed to make a request"""
        key = f"ratelimit:{user_id}"
        
        # Get current count or create if not exists
        count = self.cache.get(key, 0)
        
        if count >= self.rate:
            # Still increment the counter for tracking purposes
            cache.set(key, count + 1, self.per)
            return False
        
        count += 1
        cache.set(key, count, self.per)
        
        return True