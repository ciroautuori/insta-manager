from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum

class PostType(enum.Enum):
    FEED = "feed"
    STORY = "story" 
    REEL = "reel"

class PostStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Post(Base):
    """Modello per i post Instagram pubblicati"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    instagram_post_id = Column(String(255), unique=True, index=True, nullable=True)
    account_id = Column(Integer, ForeignKey("instagram_accounts.id"), nullable=False)
    
    # Contenuto del post
    caption = Column(Text, nullable=True)
    post_type = Column(Enum(PostType), nullable=False, default=PostType.FEED)
    status = Column(Enum(PostStatus), nullable=False, default=PostStatus.DRAFT)
    
    # Media associati
    media_urls = Column(JSON, nullable=True)  # Lista di URL media
    thumbnail_url = Column(String(500), nullable=True)
    
    # Metadati Instagram
    permalink = Column(String(500), nullable=True)
    timestamp = Column(DateTime, nullable=True)  # Data pubblicazione su Instagram
    
    # Statistiche (aggiornate periodicamente)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0, nullable=True)
    reach = Column(Integer, default=0, nullable=True)
    impressions = Column(Integer, default=0, nullable=True)
    
    # Metadati locali
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    account = relationship("InstagramAccount", back_populates="posts")
    media = relationship("Media", back_populates="post", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Post(id={self.id}, account_id={self.account_id}, type={self.post_type})>"
    
    @property
    def engagement_rate(self):
        """Calcola il tasso di engagement"""
        if not self.reach or self.reach == 0:
            return 0.0
        
        total_engagement = (self.like_count or 0) + (self.comment_count or 0) + (self.share_count or 0)
        return (total_engagement / self.reach) * 100
    
    def to_dict(self):
        """Converte il modello in dizionario"""
        return {
            "id": self.id,
            "instagram_post_id": self.instagram_post_id,
            "account_id": self.account_id,
            "caption": self.caption,
            "post_type": self.post_type,
            "media_urls": self.media_urls,
            "thumbnail_url": self.thumbnail_url,
            "permalink": self.permalink,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "share_count": self.share_count,
            "reach": self.reach,
            "impressions": self.impressions,
            "engagement_rate": self.engagement_rate,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
