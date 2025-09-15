from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.analytics import Analytics
from app.models.instagram_account import InstagramAccount
from app.schemas.analytics import AnalyticsResponse, AnalyticsPeriod, AccountInsights
from app.services.instagram_service import instagram_service

router = APIRouter()

@router.get("/", response_model=List[AnalyticsResponse])
async def get_analytics(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    account_id: Optional[int] = Query(None, description="Filtra per account ID"),
    start_date: Optional[date] = Query(None, description="Data inizio"),
    end_date: Optional[date] = Query(None, description="Data fine"),
    limit: int = Query(50, le=100, description="Numero massimo risultati")
):
    """Ottieni analytics con filtri"""
    query = db.query(Analytics)
    
    if account_id:
        query = query.filter(Analytics.account_id == account_id)
    
    if start_date:
        query = query.filter(Analytics.date >= start_date)
    
    if end_date:
        query = query.filter(Analytics.date <= end_date)
    
    analytics = query.order_by(Analytics.date.desc()).limit(limit).all()
    return analytics

@router.get("/account/{account_id}", response_model=List[AnalyticsResponse])
async def get_account_analytics(
    account_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    days: int = Query(30, description="Numero giorni da includere")
):
    """Ottieni analytics per account specifico"""
    account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    start_date = date.today() - timedelta(days=days)
    
    analytics = db.query(Analytics).filter(
        Analytics.account_id == account_id,
        Analytics.date >= start_date
    ).order_by(Analytics.date.desc()).all()
    
    return analytics

@router.post("/sync/{account_id}")
async def sync_account_analytics(
    account_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Sincronizza analytics da Instagram"""
    account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    if not account.is_business_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analytics disponibili solo per account business"
        )
    
    try:
        # Ottieni insights da Instagram (ultimi 7 giorni)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        insights_data = await instagram_service.get_account_insights(
            access_token=account.access_token,
            period="day",
            since=start_date,
            until=end_date
        )
        
        # Processa e salva analytics
        for day_data in insights_data.get('data', []):
            analytics_date = datetime.fromisoformat(day_data['end_time'].replace('Z', '+00:00')).date()
            
            # Cerca analytics esistenti per questa data
            existing = db.query(Analytics).filter(
                Analytics.account_id == account_id,
                Analytics.date == analytics_date
            ).first()
            
            if existing:
                # Aggiorna esistente
                analytics_record = existing
            else:
                # Crea nuovo
                analytics_record = Analytics(
                    account_id=account_id,
                    date=analytics_date
                )
                db.add(analytics_record)
            
            # Aggiorna metriche
            for metric in day_data.get('values', []):
                metric_name = metric['name']
                metric_value = metric['value']
                
                if metric_name == 'impressions':
                    analytics_record.total_impressions = metric_value
                elif metric_name == 'reach':
                    analytics_record.total_reach = metric_value
                elif metric_name == 'profile_views':
                    analytics_record.profile_views = metric_value
                elif metric_name == 'website_clicks':
                    analytics_record.website_clicks = metric_value
            
            # Aggiorna contatori follower
            analytics_record.followers_count = account.followers_count
            analytics_record.following_count = account.following_count
            analytics_record.posts_count = account.posts_count
        
        db.commit()
        
        return {"message": "Analytics sincronizzati con successo"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore sincronizzazione analytics: {str(e)}"
        )

@router.get("/insights/{account_id}", response_model=AccountInsights)
async def get_account_insights(
    account_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    days: int = Query(30, description="Periodo in giorni")
):
    """Ottieni insights avanzati per account"""
    account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    start_date = date.today() - timedelta(days=days)
    
    # Ottieni analytics per periodo
    analytics = db.query(Analytics).filter(
        Analytics.account_id == account_id,
        Analytics.date >= start_date
    ).order_by(Analytics.date).all()
    
    # Calcola crescita follower
    followers_growth = []
    for record in analytics:
        followers_growth.append({
            "date": record.date.isoformat(),
            "count": record.followers_count
        })
    
    # Analizza performance per tipo di post
    posts = account.posts
    engagement_by_type = {}
    
    for post in posts:
        post_type = post.post_type.value
        if post_type not in engagement_by_type:
            engagement_by_type[post_type] = {"total_engagement": 0, "total_reach": 0, "count": 0}
        
        engagement = post.likes_count + post.comments_count
        engagement_by_type[post_type]["total_engagement"] += engagement
        engagement_by_type[post_type]["total_reach"] += post.reach
        engagement_by_type[post_type]["count"] += 1
    
    # Calcola rate per tipo
    engagement_rates = {}
    for post_type, data in engagement_by_type.items():
        if data["total_reach"] > 0 and data["count"] > 0:
            rate = (data["total_engagement"] / data["total_reach"]) * 100
            engagement_rates[post_type] = round(rate, 2)
        else:
            engagement_rates[post_type] = 0.0
    
    # Migliori orari posting (simulato - richiederebbe analisi storica)
    best_posting_times = {
        "monday": 9,
        "tuesday": 10,
        "wednesday": 11,
        "thursday": 10,
        "friday": 15,
        "saturday": 12,
        "sunday": 14
    }
    
    # Performance hashtag (esempio - richiederebbe analisi dettagliata)
    hashtag_performance = [
        {"hashtag": "#instagram", "uses": 10, "avg_engagement": 250},
        {"hashtag": "#content", "uses": 8, "avg_engagement": 180},
        {"hashtag": "#social", "uses": 12, "avg_engagement": 320}
    ]
    
    return AccountInsights(
        account_id=account_id,
        username=account.username,
        followers_growth=followers_growth,
        engagement_by_post_type=engagement_rates,
        best_posting_times=best_posting_times,
        hashtag_performance=hashtag_performance
    )

@router.delete("/account/{account_id}")
async def delete_account_analytics(
    account_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    confirm: bool = Query(False, description="Conferma eliminazione")
):
    """Elimina tutti gli analytics per account"""
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Eliminazione non confermata. Usa ?confirm=true"
        )
    
    account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    # Elimina tutti gli analytics
    deleted_count = db.query(Analytics).filter(Analytics.account_id == account_id).delete()
    db.commit()
    
    return {"message": f"Eliminati {deleted_count} record analytics per account {account.username}"}

@router.get("/export/{account_id}")
async def export_analytics(
    account_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("json", description="Formato export: json, csv")
):
    """Esporta analytics in formato specificato"""
    account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    query = db.query(Analytics).filter(Analytics.account_id == account_id)
    
    if start_date:
        query = query.filter(Analytics.date >= start_date)
    if end_date:
        query = query.filter(Analytics.date <= end_date)
    
    analytics = query.order_by(Analytics.date).all()
    
    if format.lower() == "csv":
        # Genera CSV
        import io, csv
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Date", "Followers", "Following", "Posts", "Profile Views",
            "Website Clicks", "Total Likes", "Total Comments", "Total Impressions", "Total Reach"
        ])
        
        # Dati
        for record in analytics:
            writer.writerow([
                record.date,
                record.followers_count,
                record.following_count,
                record.posts_count,
                record.profile_views,
                record.website_clicks,
                record.total_likes,
                record.total_comments,
                record.total_impressions,
                record.total_reach
            ])
        
        from fastapi.responses import Response
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=analytics_{account.username}_{date.today()}.csv"}
        )
    
    # Default JSON export
    analytics_data = [
        {
            "date": record.date.isoformat(),
            "followers_count": record.followers_count,
            "following_count": record.following_count,
            "posts_count": record.posts_count,
            "profile_views": record.profile_views,
            "website_clicks": record.website_clicks,
            "total_likes": record.total_likes,
            "total_comments": record.total_comments,
            "total_impressions": record.total_impressions,
            "total_reach": record.total_reach,
            "engagement_rate": record.engagement_rate,
            "audience_demographics": record.audience_demographics
        }
        for record in analytics
    ]
    
    return {
        "account": {
            "id": account.id,
            "username": account.username
        },
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "analytics": analytics_data
    }
