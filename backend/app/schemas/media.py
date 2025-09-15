from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.media import MediaType, MediaStatus

class MediaBase(BaseModel):
    filename: str
    alt_text: Optional[str] = None
    order_index: int = 0

class MediaUpload(BaseModel):
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None

class MediaResponse(MediaBase):
    id: int
    post_id: Optional[int] = None
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    media_type: MediaType
    status: MediaStatus
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    instagram_media_id: Optional[str] = None
    thumbnail_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class MediaUpdate(BaseModel):
    alt_text: Optional[str] = None
    order_index: Optional[int] = None
