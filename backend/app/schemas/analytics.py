from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List, Dict, Any

class AnalyticsPeriod(BaseModel):
    start_date: date
    end_date: date
    account_id: Optional[int] = None

class AnalyticsResponse(BaseModel):
    id: int
    account_id: int
    date: date
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    profile_views: int = 0
    website_clicks: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_impressions: int = 0
    total_reach: int = 0
    story_impressions: int = 0
    story_reach: int = 0
    engagement_rate: Optional[Dict[str, Any]] = None
    audience_demographics: Optional[Dict[str, Any]] = None
    top_posts: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_accounts: int
    active_accounts: int
    total_followers: int
    total_posts: int
    scheduled_posts: int
    engagement_rate: float
    top_performing_accounts: List[Dict[str, Any]]

class AccountInsights(BaseModel):
    account_id: int
    username: str
    followers_growth: List[Dict[str, int]]  # [{"date": "2023-01-01", "count": 1000}]
    engagement_by_post_type: Dict[str, float]
    best_posting_times: Dict[str, int]
    hashtag_performance: List[Dict[str, Any]]
