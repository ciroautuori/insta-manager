from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("instagram_accounts.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)  # Analytics specifiche per singolo post
    
    # Period di raccolta dati
    date = Column(Date, nullable=False)  # Data per cui sono raccolti i dati
    
    # Metriche account
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    
    # Metriche di engagement
    profile_views = Column(Integer, default=0)
    website_clicks = Column(Integer, default=0)
    email_contacts = Column(Integer, default=0)
    phone_calls = Column(Integer, default=0)
    text_messages = Column(Integer, default=0)
    get_directions = Column(Integer, default=0)
    
    # Metriche dei contenuti (per il periodo)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_impressions = Column(Integer, default=0)
    total_reach = Column(Integer, default=0)
    total_saved = Column(Integer, default=0)
    
    # Demografia audience (JSON structure)
    audience_demographics = Column(JSON, nullable=True)  # Età, genere, location
    
    # Top posts del periodo
    top_posts = Column(JSON, nullable=True)  # Array di post IDs con metriche
    
    # Insights avanzati
    engagement_rate = Column(JSON, nullable=True)  # Rate per tipo di contenuto
    best_posting_times = Column(JSON, nullable=True)  # Migliori orari posting
    hashtag_performance = Column(JSON, nullable=True)  # Performance hashtags
    
    # Story metrics (se disponibili)
    story_impressions = Column(Integer, default=0)
    story_reach = Column(Integer, default=0)
    story_replies = Column(Integer, default=0)
    story_exits = Column(Integer, default=0)
    
    # Raw data from Instagram API
    raw_insights_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    account = relationship("InstagramAccount", back_populates="analytics")
    post = relationship("Post", back_populates="analytics")
