"""
Rate limiter to prevent exceeding API quotas.
Implements token bucket algorithm for rate limiting.
"""
import time
from threading import Lock
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter to prevent API quota exhaustion.
    
    For Gemini free tier:
    - gemini-2.0-flash-exp: 15 requests per minute
    - gemini-2.5-pro: 50 requests per day (very restrictive)
    """
    
    def __init__(self, max_requests: int = 12, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in time_window
            time_window: Time window in seconds (default: 60 for per-minute limits)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.tokens = max_requests
        self.last_refill = time.time()
        self.lock = Lock()
        
    def acquire(self, wait: bool = True) -> bool:
        """
        Try to acquire a token (permit a request).
        
        Args:
            wait: If True, wait until token is available. If False, return immediately.
            
        Returns:
            True if token acquired, False otherwise
        """
        with self.lock:
            self._refill_tokens()
            
            if self.tokens > 0:
                self.tokens -= 1
                logger.debug(f"Token acquired. Remaining: {self.tokens}/{self.max_requests}")
                return True
            
            if not wait:
                logger.warning(f"Rate limit exceeded. No tokens available.")
                return False
            
            # Calculate wait time
            wait_time = self.time_window - (time.time() - self.last_refill)
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                return self.acquire(wait=False)
            
            return False
    
    def _refill_tokens(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        if elapsed >= self.time_window:
            # Full refill
            self.tokens = self.max_requests
            self.last_refill = now
            logger.debug(f"Tokens refilled to {self.max_requests}")
        else:
            # Partial refill based on elapsed time
            tokens_to_add = int((elapsed / self.time_window) * self.max_requests)
            if tokens_to_add > 0:
                self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
                self.last_refill = now
    
    def get_available_tokens(self) -> int:
        """Get current number of available tokens."""
        with self.lock:
            self._refill_tokens()
            return self.tokens


# Global rate limiter instance
# Conservative: 12 requests per minute (80% of 15/min limit for gemini-2.0-flash-exp)
_rate_limiter = RateLimiter(max_requests=12, time_window=60)


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter

