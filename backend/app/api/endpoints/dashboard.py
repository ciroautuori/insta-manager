from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.instagram_account import InstagramAccount
from app.models.post import Post, PostStatus
from app.models.scheduled_post import ScheduledPost, ScheduleStatus
from app.models.analytics import Analytics
from app.schemas.analytics import DashboardStats

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ottieni statistiche generali dashboard"""
    
    # Conteggi base
    total_accounts = db.query(InstagramAccount).count()
    active_accounts = db.query(InstagramAccount).filter(InstagramAccount.is_active == True).count()
    
    # Totale follower
    total_followers = db.query(func.sum(InstagramAccount.followers_count)).scalar() or 0
    
    # Totale post
    total_posts = db.query(Post).filter(Post.status == "published").count()
    
    # Post programmati (pending)
    scheduled_posts = db.query(ScheduledPost).filter(ScheduledPost.status == ScheduleStatus.PENDING).count()

    # Calcola engagement rate medio
    posts_with_metrics = db.query(Post).filter(
        Post.status == "published",
        Post.reach > 0
    ).all()
    
    total_engagement = sum(p.like_count + p.comment_count for p in posts_with_metrics)
    total_reach = sum(p.reach for p in posts_with_metrics)
    engagement_rate = (total_engagement / total_reach) * 100 if total_reach > 0 else 0.0
    
    # Top performing accounts
    accounts_stats = []
    accounts = db.query(InstagramAccount).filter(InstagramAccount.is_active == True).all()
    
    for account in accounts:
        account_posts = [p for p in account.posts if p.status == "published" and p.reach > 0]
        account_engagement = sum(p.like_count + p.comment_count for p in account_posts)
        account_reach = sum(p.reach for p in account_posts)
        account_rate = (account_engagement / account_reach) * 100 if account_reach > 0 else 0.0
        
        accounts_stats.append({
            "id": account.id,
            "username": account.username,
            "followers_count": account.followers_count,
            "posts_count": len(account_posts),
            "engagement_rate": round(account_rate, 2)
        })
    
    # Ordina per engagement rate e prendi top 5
    top_accounts = sorted(accounts_stats, key=lambda x: x["engagement_rate"], reverse=True)[:5]
    
    return DashboardStats(
        total_accounts=total_accounts,
        active_accounts=active_accounts,
        total_followers=total_followers,
        total_posts=total_posts,
        scheduled_posts=scheduled_posts,
        engagement_rate=round(engagement_rate, 2),
        top_performing_accounts=top_accounts
    )

@router.get("/recent-activity")
async def get_recent_activity(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """Ottieni attività recenti"""
    
    # Post pubblicati di recente
    recent_posts = db.query(Post).filter(
        Post.status == "published",
        Post.timestamp.isnot(None)
    ).order_by(Post.timestamp.desc()).limit(limit).all()
    
    # Post programmati prossimi (entro i prossimi 7 giorni)
    now = datetime.utcnow()
    upcoming_scheduled = db.query(ScheduledPost).filter(
        ScheduledPost.status == ScheduleStatus.PENDING,
        ScheduledPost.scheduled_for >= now,
        ScheduledPost.scheduled_for <= now + timedelta(days=7)
    ).order_by(ScheduledPost.scheduled_for.asc()).limit(10).all()
    
    # Account connessi di recente
    recent_accounts = db.query(InstagramAccount).order_by(
        InstagramAccount.created_at.desc()
    ).limit(5).all()
    
    activity = {
        "recent_posts": [
            {
                "id": p.id,
                "caption": p.caption[:50] + "..." if p.caption and len(p.caption) > 50 else p.caption,
                "account_username": p.account.username,
                "published_at": p.timestamp,
                "likes_count": p.like_count,
                "comments_count": p.comment_count
            }
            for p in recent_posts
        ],
        "upcoming_scheduled": [
            {
                "id": s.id,
                "caption": s.caption[:50] + "..." if s.caption and len(s.caption) > 50 else s.caption,
                "account_username": s.account.username,
                "scheduled_for": s.scheduled_for,
                "status": s.status
            }
            for s in upcoming_scheduled
        ],
        "recent_accounts": [
            {
                "id": a.id,
                "username": a.username,
                "followers_count": a.followers_count,
                "connected_at": a.created_at
            }
            for a in recent_accounts
        ]
    }
    
    return activity

@router.get("/performance-metrics")
async def get_performance_metrics(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Ottieni metriche performance ultimi N giorni"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Posts nel periodo
    period_posts = db.query(Post).filter(
        Post.timestamp >= start_date,
        Post.status == "published"
    ).all()
    
    # Metriche aggregate
    metrics = {
        "period_days": days,
        "total_posts": len(period_posts),
        "total_likes": sum(p.like_count for p in period_posts),
        "total_comments": sum(p.comment_count for p in period_posts),
        "total_impressions": sum(p.impressions for p in period_posts),
        "total_reach": sum(p.reach for p in period_posts),
        "avg_engagement_rate": 0.0
    }
    
    # Calcola engagement rate medio
    if metrics["total_reach"] > 0:
        total_engagement = metrics["total_likes"] + metrics["total_comments"]
        metrics["avg_engagement_rate"] = round((total_engagement / metrics["total_reach"]) * 100, 2)
    
    # Performance per giorno (ultimi 7 giorni)
    daily_performance = []
    for i in range(7):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        day_posts = [p for p in period_posts if day_start <= p.timestamp < day_end]
        
        daily_performance.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "posts_count": len(day_posts),
            "likes": sum(p.like_count for p in day_posts),
            "comments": sum(p.comment_count for p in day_posts),
            "impressions": sum(p.impressions for p in day_posts)
        })
    
    metrics["daily_performance"] = list(reversed(daily_performance))
    
    return metrics

@router.get("/content-insights")
async def get_content_insights(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ottieni insights contenuti"""
    
    # Analizza tutti i post pubblicati
    published_posts = db.query(Post).filter(Post.status == "published").all()
    
    # Performance per tipo di post
    post_type_performance = {}
    for post in published_posts:
        post_type = post.post_type.value
        if post_type not in post_type_performance:
            post_type_performance[post_type] = {
                "count": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_reach": 0
            }
        
        post_type_performance[post_type]["count"] += 1
        post_type_performance[post_type]["total_likes"] += (post.like_count or 0)
        post_type_performance[post_type]["total_comments"] += (post.comment_count or 0)
        post_type_performance[post_type]["total_reach"] += (post.reach or 0)
    
    # Calcola medie per tipo
    for post_type, stats in post_type_performance.items():
        if stats["count"] > 0:
            stats["avg_likes"] = round(stats["total_likes"] / stats["count"], 1)
            stats["avg_comments"] = round(stats["total_comments"] / stats["count"], 1)
            stats["avg_engagement_rate"] = round(
                ((stats["total_likes"] + stats["total_comments"]) / stats["total_reach"]) * 100, 2
            ) if stats["total_reach"] > 0 else 0.0
    
    # Top hashtags (analisi semplificata)
    hashtag_usage = {}
    for post in published_posts:
        # Il modello Post non espone hashtags; questa sezione è opzionale
        if hasattr(post, 'hashtags') and getattr(post, 'hashtags'):
            for hashtag in getattr(post, 'hashtags'):
                if hashtag not in hashtag_usage:
                    hashtag_usage[hashtag] = {"count": 0, "total_engagement": 0}
                
                hashtag_usage[hashtag]["count"] += 1
                hashtag_usage[hashtag]["total_engagement"] += (post.like_count or 0) + (post.comment_count or 0)
    
    # Top 10 hashtags per utilizzo
    top_hashtags = sorted(
        [{"hashtag": tag, **stats} for tag, stats in hashtag_usage.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:10]
    
    # Migliori orari posting (analisi semplificata)
    hour_performance = {}
    for post in published_posts:
        if post.timestamp:
            hour = post.timestamp.hour
            if hour not in hour_performance:
                hour_performance[hour] = {"count": 0, "total_engagement": 0}
            
            hour_performance[hour]["count"] += 1
            hour_performance[hour]["total_engagement"] += post.like_count + post.comment_count
    
    # Calcola engagement medio per ora
    best_hours = []
    for hour, stats in hour_performance.items():
        if stats["count"] >= 3:  # Minimo 3 post per considerare l'ora
            avg_engagement = stats["total_engagement"] / stats["count"]
            best_hours.append({
                "hour": f"{hour:02d}:00",
                "avg_engagement": round(avg_engagement, 1),
                "posts_count": stats["count"]
            })
    
    best_hours = sorted(best_hours, key=lambda x: x["avg_engagement"], reverse=True)[:5]
    
    return {
        "post_type_performance": post_type_performance,
        "top_hashtags": top_hashtags,
        "best_posting_hours": best_hours,
        "total_analyzed_posts": len(published_posts)
    }

@router.get("/health")
async def health_check():
    """Health check endpoint per dashboard"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "instagram-manager-api"
    }
