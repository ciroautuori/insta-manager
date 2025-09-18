from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from app.core.logging import get_logger

logger = get_logger(__name__)


class InstagramManagerException(Exception):
    """Base exception for Instagram Manager application."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(InstagramManagerException):
    """Raised when input validation fails."""
    pass


class AuthenticationError(InstagramManagerException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(InstagramManagerException):
    """Raised when user lacks required permissions."""
    pass


class InstagramAPIError(InstagramManagerException):
    """Raised when Instagram API calls fail."""
    
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(message, {"status_code": status_code, "response_data": response_data})


class RateLimitError(InstagramManagerException):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(message, {"retry_after": retry_after})


class DatabaseError(InstagramManagerException):
    """Raised when database operations fail."""
    pass


class MediaProcessingError(InstagramManagerException):
    """Raised when media processing fails."""
    pass


class SchedulingError(InstagramManagerException):
    """Raised when post scheduling fails."""
    pass


def create_http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """Create standardized HTTP exception with logging."""
    
    error_data = {
        "error": True,
        "message": message,
        "status_code": status_code
    }
    
    if details:
        error_data["details"] = details
    
    # Log the error
    logger.error(
        f"HTTP {status_code}: {message}",
        extra={"status_code": status_code, "details": details}
    )
    
    return HTTPException(status_code=status_code, detail=error_data)


def validation_error(message: str, field: str = None) -> HTTPException:
    """Create validation error response."""
    details = {"field": field} if field else None
    return create_http_exception(
        status.HTTP_400_BAD_REQUEST,
        message,
        details
    )


def authentication_error(message: str = "Authentication required") -> HTTPException:
    """Create authentication error response."""
    return create_http_exception(
        status.HTTP_401_UNAUTHORIZED,
        message
    )


def authorization_error(message: str = "Insufficient permissions") -> HTTPException:
    """Create authorization error response."""
    return create_http_exception(
        status.HTTP_403_FORBIDDEN,
        message
    )


def not_found_error(resource: str, identifier: Any = None) -> HTTPException:
    """Create not found error response."""
    message = f"{resource} not found"
    if identifier:
        message += f" (ID: {identifier})"
    
    return create_http_exception(
        status.HTTP_404_NOT_FOUND,
        message,
        {"resource": resource, "identifier": identifier}
    )


def conflict_error(message: str, resource: str = None) -> HTTPException:
    """Create conflict error response."""
    details = {"resource": resource} if resource else None
    return create_http_exception(
        status.HTTP_409_CONFLICT,
        message,
        details
    )


def rate_limit_error(message: str = "Rate limit exceeded", retry_after: int = None) -> HTTPException:
    """Create rate limit error response."""
    headers = {"Retry-After": str(retry_after)} if retry_after else None
    
    error_data = {
        "error": True,
        "message": message,
        "status_code": status.HTTP_429_TOO_MANY_REQUESTS
    }
    
    if retry_after:
        error_data["retry_after"] = retry_after
    
    logger.warning(
        f"Rate limit exceeded: {message}",
        extra={"retry_after": retry_after}
    )
    
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=error_data,
        headers=headers
    )


def server_error(message: str = "Internal server error", details: Dict = None) -> HTTPException:
    """Create server error response."""
    return create_http_exception(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        message,
        details
    )


def instagram_api_error(message: str, api_status_code: int = None) -> HTTPException:
    """Create Instagram API error response."""
    details = {"instagram_status_code": api_status_code} if api_status_code else None
    
    # Map Instagram API errors to appropriate HTTP status codes
    if api_status_code == 400:
        status_code = status.HTTP_400_BAD_REQUEST
    elif api_status_code == 401:
        status_code = status.HTTP_401_UNAUTHORIZED
    elif api_status_code == 403:
        status_code = status.HTTP_403_FORBIDDEN
    elif api_status_code == 429:
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    else:
        status_code = status.HTTP_502_BAD_GATEWAY
    
    return create_http_exception(status_code, message, details)
