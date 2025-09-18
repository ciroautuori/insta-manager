from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from pydantic import BaseModel, validator, ValidationError
from fastapi import HTTPException, status
import re
from pathlib import Path

from app.core.exceptions import validation_error
from app.core.logging import get_logger

logger = get_logger(__name__)


class ValidationMixin:
    """Mixin for adding validation methods to Pydantic models."""
    
    @validator('email', pre=True, always=True)
    def validate_email(cls, v):
        """Validate email format."""
        if not v:
            raise ValueError('Email is required')
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        
        return v.lower()
    
    @validator('password', pre=True, always=True)
    def validate_password(cls, v):
        """Validate password strength."""
        if not v:
            raise ValueError('Password is required')
        
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        return v


def validate_future_datetime(dt: datetime) -> datetime:
    """Validate that datetime is in the future."""
    if dt <= datetime.utcnow():
        raise validation_error("Scheduled time must be in the future")
    return dt


def validate_media_file(file_path: str) -> str:
    """Validate media file path and format."""
    if not file_path:
        raise validation_error("Media file path is required")
    
    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov'}
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise validation_error(
            f"Unsupported file format: {file_ext}. "
            f"Allowed formats: {', '.join(allowed_extensions)}"
        )
    
    return file_path


def validate_caption(caption: str, max_length: int = 2200) -> str:
    """Validate Instagram caption."""
    if not caption or not caption.strip():
        raise validation_error("Caption cannot be empty")
    
    if len(caption) > max_length:
        raise validation_error(f"Caption too long. Maximum {max_length} characters allowed")
    
    return caption.strip()


def validate_hashtags(hashtags: List[str]) -> List[str]:
    """Validate Instagram hashtags."""
    if not hashtags:
        return []
    
    if len(hashtags) > 30:
        raise validation_error("Maximum 30 hashtags allowed")
    
    validated_hashtags = []
    hashtag_pattern = r'^[a-zA-Z0-9_]+$'
    
    for hashtag in hashtags:
        # Remove # if present
        clean_hashtag = hashtag.lstrip('#')
        
        if not clean_hashtag:
            continue
        
        if len(clean_hashtag) > 100:
            raise validation_error(f"Hashtag too long: #{clean_hashtag}")
        
        if not re.match(hashtag_pattern, clean_hashtag):
            raise validation_error(f"Invalid hashtag format: #{clean_hashtag}")
        
        validated_hashtags.append(clean_hashtag)
    
    return validated_hashtags


def validate_account_id(account_id: int, db_session) -> int:
    """Validate that account exists and is active."""
    from app.models.instagram_account import InstagramAccount
    
    account = db_session.query(InstagramAccount).filter(
        InstagramAccount.id == account_id,
        InstagramAccount.is_active == True
    ).first()
    
    if not account:
        raise validation_error(f"Active Instagram account not found: {account_id}")
    
    return account_id


def validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> tuple:
    """Validate date range parameters."""
    if start_date and end_date:
        if start_date > end_date:
            raise validation_error("Start date cannot be after end date")
        
        # Limit date range to prevent performance issues
        if (end_date - start_date).days > 365:
            raise validation_error("Date range cannot exceed 365 days")
    
    return start_date, end_date


def validate_pagination(page: int = 1, per_page: int = 20) -> tuple:
    """Validate pagination parameters."""
    if page < 1:
        raise validation_error("Page number must be positive")
    
    if per_page < 1 or per_page > 100:
        raise validation_error("Per page must be between 1 and 100")
    
    return page, per_page


def validate_instagram_username(username: str) -> str:
    """Validate Instagram username format."""
    if not username:
        raise validation_error("Username is required")
    
    # Instagram username rules
    username_pattern = r'^[a-zA-Z0-9._]{1,30}$'
    if not re.match(username_pattern, username):
        raise validation_error(
            "Invalid username format. Use only letters, numbers, periods, and underscores"
        )
    
    if username.startswith('.') or username.endswith('.'):
        raise validation_error("Username cannot start or end with a period")
    
    if '..' in username:
        raise validation_error("Username cannot contain consecutive periods")
    
    return username.lower()


def validate_post_type(post_type: str) -> str:
    """Validate Instagram post type."""
    allowed_types = {'FEED', 'STORY', 'REEL', 'IGTV'}
    
    if post_type not in allowed_types:
        raise validation_error(f"Invalid post type. Allowed: {', '.join(allowed_types)}")
    
    return post_type


def validate_scheduling_interval(interval_minutes: int) -> int:
    """Validate scheduling interval."""
    if interval_minutes < 5:
        raise validation_error("Minimum scheduling interval is 5 minutes")
    
    if interval_minutes > 10080:  # 1 week
        raise validation_error("Maximum scheduling interval is 1 week")
    
    return interval_minutes


def validate_json_field(data: Any, field_name: str) -> Dict:
    """Validate JSON field data."""
    if data is None:
        return {}
    
    if isinstance(data, str):
        try:
            import json
            data = json.loads(data)
        except json.JSONDecodeError:
            raise validation_error(f"Invalid JSON format in {field_name}")
    
    if not isinstance(data, dict):
        raise validation_error(f"{field_name} must be a JSON object")
    
    return data


class BulkOperationValidator:
    """Validator for bulk operations."""
    
    @staticmethod
    def validate_bulk_size(items: List[Any], max_size: int = 50) -> List[Any]:
        """Validate bulk operation size."""
        if not items:
            raise validation_error("No items provided for bulk operation")
        
        if len(items) > max_size:
            raise validation_error(f"Bulk operation size exceeds limit: {len(items)} > {max_size}")
        
        return items
    
    @staticmethod
    def validate_bulk_posts(posts_data: List[Dict]) -> List[Dict]:
        """Validate bulk post creation data."""
        validated_posts = []
        
        for i, post_data in enumerate(posts_data):
            try:
                # Validate required fields
                if 'caption' not in post_data:
                    raise ValueError("Caption is required")
                
                if 'media_files' not in post_data or not post_data['media_files']:
                    raise ValueError("At least one media file is required")
                
                if 'scheduled_for' not in post_data:
                    raise ValueError("Scheduled time is required")
                
                # Validate individual fields
                validate_caption(post_data['caption'])
                
                for media_file in post_data['media_files']:
                    validate_media_file(media_file)
                
                scheduled_time = datetime.fromisoformat(post_data['scheduled_for'].replace('Z', '+00:00'))
                validate_future_datetime(scheduled_time)
                
                validated_posts.append(post_data)
                
            except (ValueError, ValidationError) as e:
                raise validation_error(f"Validation error in post {i+1}: {str(e)}")
        
        return validated_posts


def handle_validation_error(func):
    """Decorator to handle validation errors in API endpoints."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            raise validation_error(str(e))
        except ValueError as e:
            logger.warning(f"Value error in {func.__name__}: {str(e)}")
            raise validation_error(str(e))
    
    return wrapper
