"""
Advanced rate limiting and security hardening utilities.
"""
import time
import hashlib
import secrets
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status
from fastapi.security.utils import get_authorization_scheme_param
import redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class SecurityHardening:
    """Security hardening utilities and middleware."""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.failed_attempts_key = "failed_login_attempts"
        self.blocked_ips_key = "blocked_ips"
        self.suspicious_activity_key = "suspicious_activity"
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked."""
        blocked_until = self.redis_client.hget(self.blocked_ips_key, ip_address)
        if blocked_until:
            if datetime.utcnow().timestamp() < float(blocked_until):
                return True
            else:
                # Unblock expired IP
                self.redis_client.hdel(self.blocked_ips_key, ip_address)
        return False
    
    def block_ip(self, ip_address: str, duration_minutes: int = 30):
        """Block IP address for specified duration."""
        block_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.redis_client.hset(
            self.blocked_ips_key, 
            ip_address, 
            block_until.timestamp()
        )
        logger.warning(f"IP {ip_address} blocked for {duration_minutes} minutes")
    
    def record_failed_login(self, ip_address: str, email: str = None) -> int:
        """Record failed login attempt and return current count."""
        key = f"{self.failed_attempts_key}:{ip_address}"
        current_count = self.redis_client.incr(key)
        
        if current_count == 1:
            # Set expiration for first attempt
            self.redis_client.expire(key, 3600)  # 1 hour
        
        # Log suspicious activity
        if email:
            logger.warning(f"Failed login attempt for {email} from {ip_address}")
        
        # Block IP after 5 failed attempts
        if current_count >= 5:
            self.block_ip(ip_address, 60)  # Block for 1 hour
            logger.critical(f"IP {ip_address} blocked after {current_count} failed attempts")
        
        return current_count
    
    def clear_failed_attempts(self, ip_address: str):
        """Clear failed login attempts for IP."""
        key = f"{self.failed_attempts_key}:{ip_address}"
        self.redis_client.delete(key)
    
    def detect_brute_force(self, ip_address: str, endpoint: str) -> bool:
        """Detect potential brute force attacks."""
        key = f"endpoint_requests:{ip_address}:{endpoint}"
        request_count = self.redis_client.incr(key)
        
        if request_count == 1:
            self.redis_client.expire(key, 300)  # 5 minutes window
        
        # More than 20 requests to same endpoint in 5 minutes
        if request_count > 20:
            self.block_ip(ip_address, 30)
            logger.critical(f"Brute force detected from {ip_address} on {endpoint}")
            return True
        
        return False
    
    def validate_jwt_claims(self, payload: dict) -> bool:
        """Validate JWT token claims for security."""
        required_claims = ['sub', 'exp', 'iat']
        
        for claim in required_claims:
            if claim not in payload:
                logger.warning(f"Missing required JWT claim: {claim}")
                return False
        
        # Check token age
        issued_at = payload.get('iat')
        if issued_at:
            token_age = datetime.utcnow().timestamp() - issued_at
            if token_age > 86400:  # 24 hours
                logger.warning("JWT token too old")
                return False
        
        return True
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session."""
        token_data = f"{session_id}:{secrets.token_urlsafe(32)}:{time.time()}"
        csrf_token = hashlib.sha256(token_data.encode()).hexdigest()
        
        # Store in Redis with expiration
        self.redis_client.setex(f"csrf_token:{session_id}", 3600, csrf_token)
        return csrf_token
    
    def validate_csrf_token(self, session_id: str, token: str) -> bool:
        """Validate CSRF token."""
        stored_token = self.redis_client.get(f"csrf_token:{session_id}")
        if stored_token and stored_token.decode() == token:
            return True
        return False

class AdvancedRateLimiter:
    """Advanced rate limiting with different strategies."""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    def sliding_window_limit(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int,
        identifier: str = None
    ) -> tuple[bool, dict]:
        """
        Sliding window rate limiting.
        Returns (is_allowed, info_dict)
        """
        now = time.time()
        pipeline = self.redis_client.pipeline()
        
        # Remove expired entries
        pipeline.zremrangebyscore(key, 0, now - window_seconds)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {f"{now}:{secrets.token_hex(8)}": now})
        
        # Set expiration
        pipeline.expire(key, window_seconds)
        
        results = pipeline.execute()
        current_count = results[1] + 1  # +1 for the request we just added
        
        is_allowed = current_count <= limit
        
        if not is_allowed and identifier:
            logger.warning(f"Rate limit exceeded for {identifier}: {current_count}/{limit}")
        
        return is_allowed, {
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "reset_time": int(now + window_seconds),
            "current_count": current_count
        }
    
    def token_bucket_limit(
        self, 
        key: str, 
        capacity: int, 
        refill_rate: float,
        identifier: str = None
    ) -> tuple[bool, dict]:
        """
        Token bucket rate limiting.
        Returns (is_allowed, info_dict)
        """
        now = time.time()
        
        # Get current bucket state
        bucket_data = self.redis_client.hmget(key, ["tokens", "last_refill"])
        
        if bucket_data[0] is None:
            # Initialize bucket
            tokens = capacity - 1  # Consume one token for this request
            last_refill = now
        else:
            tokens = float(bucket_data[0])
            last_refill = float(bucket_data[1])
            
            # Calculate tokens to add
            time_passed = now - last_refill
            tokens_to_add = time_passed * refill_rate
            tokens = min(capacity, tokens + tokens_to_add)
            
            # Consume one token
            tokens -= 1
        
        is_allowed = tokens >= 0
        
        if is_allowed:
            # Update bucket state
            self.redis_client.hmset(key, {
                "tokens": max(0, tokens),
                "last_refill": now
            })
            self.redis_client.expire(key, int(capacity / refill_rate) + 60)
        elif identifier:
            logger.warning(f"Token bucket limit exceeded for {identifier}")
        
        return is_allowed, {
            "tokens_remaining": max(0, int(tokens)),
            "capacity": capacity,
            "refill_rate": refill_rate
        }
    
    def adaptive_rate_limit(
        self, 
        key: str, 
        base_limit: int,
        window_seconds: int,
        identifier: str = None
    ) -> tuple[bool, dict]:
        """
        Adaptive rate limiting that adjusts based on system load.
        """
        # Get system metrics (simplified)
        cpu_usage = 0.5  # This would come from actual system monitoring
        memory_usage = 0.6
        
        # Adjust limit based on system load
        load_factor = max(cpu_usage, memory_usage)
        adjusted_limit = int(base_limit * (1 - load_factor * 0.5))
        adjusted_limit = max(1, adjusted_limit)  # Minimum of 1 request
        
        return self.sliding_window_limit(
            key, 
            adjusted_limit, 
            window_seconds, 
            identifier
        )

# Global instances
security_hardening = SecurityHardening()
rate_limiter = AdvancedRateLimiter()

def check_security_middleware(request: Request):
    """Security middleware to check for blocked IPs and suspicious activity."""
    client_ip = request.client.host
    
    # Check if IP is blocked
    if security_hardening.is_ip_blocked(client_ip):
        logger.warning(f"Blocked IP {client_ip} attempted access")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="IP address temporarily blocked due to suspicious activity"
        )
    
    # Check for brute force on sensitive endpoints
    sensitive_endpoints = ["/api/v1/auth/login", "/api/v1/auth/register"]
    if request.url.path in sensitive_endpoints:
        if security_hardening.detect_brute_force(client_ip, request.url.path):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests to sensitive endpoint"
            )
    
    return True
