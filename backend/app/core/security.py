from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db as get_database
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer scheme
security = HTTPBearer()

# Rate limiter with Redis
redis_client = redis.from_url(settings.REDIS_URL)
limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_database)):
    """Dependency to verify authenticated admin"""
    from app.models.admin import Admin
    
    token = credentials.credentials
    payload = verify_token(token)
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Verify that the user exists in the database as admin
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: authorized admins only"
        )
    
    return {"email": email, "role": "admin", "id": admin.id}

def check_instagram_token_validity(access_token: str) -> bool:
    """Verify Instagram token validity"""
    # Implementation to verify Meta Graph API token
    # This function will be implemented in the Instagram service
    return True

class RateLimitManager:
    """Custom rate limiting management"""
    
    @staticmethod
    def check_instagram_api_limit(user_id: int) -> bool:
        """Check Instagram API limit for user"""
        key = f"instagram_api_limit:{user_id}"
        current_count = redis_client.get(key)
        
        if current_count is None:
            redis_client.setex(key, 3600, 1)  # 1 hour
            return True
        
        if int(current_count) >= settings.INSTAGRAM_API_REQUESTS_PER_HOUR:
            return False
        
        redis_client.incr(key)
        return True
    
    @staticmethod
    def increment_api_usage(user_id: int):
        """Increment API usage counter"""
        key = f"instagram_api_limit:{user_id}"
        if redis_client.exists(key):
            redis_client.incr(key)
        else:
            redis_client.setex(key, 3600, 1)
