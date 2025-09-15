from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class InstagramAccountBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None

class InstagramAccountCreate(InstagramAccountBase):
    instagram_user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    permissions: Optional[List[str]] = None

class InstagramAccountUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None

class InstagramAccountResponse(InstagramAccountBase):
    id: int
    instagram_user_id: str
    profile_picture_url: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    is_active: bool = True
    is_business_account: bool = False
    last_sync: Optional[datetime] = None
    created_at: datetime
    permissions: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

class InstagramAuthURL(BaseModel):
    auth_url: str
    state: str

class InstagramTokenExchange(BaseModel):
    code: str
    state: str

class InstagramAccountStats(BaseModel):
    account_id: int
    username: str
    followers_count: int
    posts_count: int
    engagement_rate: float
    last_post_date: Optional[datetime] = None
