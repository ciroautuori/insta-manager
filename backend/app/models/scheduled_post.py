from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class ScheduleStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("instagram_accounts.id"), nullable=False)
    
    # Contenuto programmato
    caption = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True)  # Lista di hashtag
    post_type = Column(String, nullable=False, default="feed")  # feed, story, reel
    
    # Media files (JSON array di percorsi file)
    media_files = Column(JSON, nullable=True)
    
    # Scheduling
    scheduled_for = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(ScheduleStatus), nullable=False, default=ScheduleStatus.PENDING)
    
    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_error = Column(Text, nullable=True)
    
    # Location data
    location_id = Column(String, nullable=True)
    location_name = Column(String, nullable=True)
    
    # Risultato pubblicazione
    published_post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    instagram_post_id = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Celery task tracking
    celery_task_id = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    account = relationship("InstagramAccount", back_populates="scheduled_posts")
    published_post = relationship("Post", foreign_keys=[published_post_id])
