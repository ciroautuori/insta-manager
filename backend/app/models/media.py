from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"

class MediaStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    
    # File info
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    mime_type = Column(String, nullable=False)
    
    # Media properties
    media_type = Column(Enum(MediaType), nullable=False)
    status = Column(Enum(MediaStatus), nullable=False, default=MediaStatus.UPLOADED)
    
    # Image/Video metadata
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  # For videos, in seconds
    
    # Instagram media ID (dopo upload su Instagram)
    instagram_media_id = Column(String, nullable=True)
    
    # Thumbnail (per video)
    thumbnail_path = Column(String, nullable=True)
    
    # Alt text per accessibilità
    alt_text = Column(Text, nullable=True)
    
    # Order nel caso di carousel
    order_index = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="media")
