from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class InstagramAccount(Base):
    __tablename__ = "instagram_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    instagram_user_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    
    # OAuth tokens
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Permissions e scopes
    permissions = Column(JSON, nullable=True)  # Lista dei permessi concessi
    
    # Status
    is_active = Column(Boolean, default=True)
    is_business_account = Column(Boolean, default=False)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    posts = relationship("Post", back_populates="account", cascade="all, delete-orphan")
    scheduled_posts = relationship("ScheduledPost", back_populates="account", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="account", cascade="all, delete-orphan")
