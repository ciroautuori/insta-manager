from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.post import PostType, PostStatus

class PostBase(BaseModel):
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    post_type: PostType = PostType.FEED
    location_id: Optional[str] = None
    location_name: Optional[str] = None

class PostCreate(PostBase):
    account_id: int
    media_files: Optional[List[int]] = None  # IDs dei media caricati

class PostUpdate(BaseModel):
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    status: Optional[PostStatus] = None

class PostResponse(PostBase):
    id: int
    account_id: int
    instagram_post_id: Optional[str] = None
    status: PostStatus
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    impressions: int = 0
    reach: int = 0
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PostStats(BaseModel):
    total_posts: int
    published_posts: int
    draft_posts: int
    failed_posts: int
    total_likes: int
    total_comments: int
    engagement_rate: float

class PostAnalytics(BaseModel):
    post_id: int
    likes_count: int
    comments_count: int
    shares_count: int
    impressions: int
    reach: int
    engagement_rate: float
    posted_at: datetime
