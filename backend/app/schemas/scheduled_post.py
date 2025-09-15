from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.scheduled_post import ScheduleStatus

class ScheduledPostBase(BaseModel):
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    post_type: str = "feed"
    location_id: Optional[str] = None
    location_name: Optional[str] = None

class ScheduledPostCreate(ScheduledPostBase):
    account_id: int
    scheduled_for: datetime
    media_files: Optional[List[str]] = None  # Percorsi dei file media

class ScheduledPostUpdate(BaseModel):
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    scheduled_for: Optional[datetime] = None
    status: Optional[ScheduleStatus] = None
    location_id: Optional[str] = None
    location_name: Optional[str] = None

class ScheduledPostResponse(ScheduledPostBase):
    id: int
    account_id: int
    scheduled_for: datetime
    status: ScheduleStatus
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    published_post_id: Optional[int] = None
    instagram_post_id: Optional[str] = None
    published_at: Optional[datetime] = None
    celery_task_id: Optional[str] = None
    created_at: datetime
    media_files: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

class ScheduledPostStats(BaseModel):
    total_scheduled: int
    pending: int
    published: int
    failed: int
    cancelled: int
