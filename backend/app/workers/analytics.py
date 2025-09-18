from celery import current_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, date, timedelta
from loguru import logger

from app.core.config import settings
from app.models.instagram_account import InstagramAccount
from app.models.analytics import Analytics
from app.models.post import Post, PostStatus
from app.services.instagram_service import instagram_service
from app.workers.celery_app import celery_app

# Database session per workers
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task(bind=True, name="sync_account_analytics")
def sync_account_analytics(self, account_id: int, days_back: int = 7):
    """Sincronizza analytics per un account specifico"""
    db = SessionLocal()
    
    try:
        account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
        if not account or not account.is_active:
            logger.warning(f"Account {account_id} non trovato o non attivo")
            return {"status": "skipped", "message": "Account non attivo"}
        
        if not account.is_business_account:
            logger.info(f"Account {account_id} non è business, skip analytics")
            return {"status": "skipped", "message": "Account non business"}
        
        # Verifica validità token
        if not instagram_service.validate_token(account.access_token):
            logger.error(f"Token non valido per account {account_id}")
            return {"status": "error", "message": "Token non valido"}
        
        # Sincronizza ultimi N giorni
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Usa versione sincrona per Celery
        insights_data = instagram_service.get_account_insights_sync(
            access_token=account.access_token,
            period="day",
            since=start_date,
            until=end_date
        )
        
        synced_records = 0
        
        # Processa insights per ogni giorno
        for day_data in insights_data.get('data', []):
            try:
                # Parse data
                end_time = day_data.get('end_time', '')
                if not end_time:
                    continue
                
                analytics_date = datetime.fromisoformat(end_time.replace('Z', '+00:00')).date()
                
                # Cerca record esistente
                existing = db.query(Analytics).filter(
                    Analytics.account_id == account_id,
                    Analytics.date == analytics_date
                ).first()
                
                if existing:
                    analytics_record = existing
                else:
                    analytics_record = Analytics(
                        account_id=account_id,
                        date=analytics_date
                    )
                    db.add(analytics_record)
                
                # Aggiorna metriche base
                analytics_record.followers_count = account.followers_count
                analytics_record.following_count = account.following_count
                analytics_record.posts_count = account.posts_count
                
                # Processa valori insights
                values = day_data.get('values', [])
                for value in values:
                    metric_name = value.get('name', '')
                    metric_value = value.get('value', 0)
                    
                    if metric_name == 'impressions':
                        analytics_record.total_impressions = metric_value
                    elif metric_name == 'reach':
                        analytics_record.total_reach = metric_value
                    elif metric_name == 'profile_views':
                        analytics_record.profile_views = metric_value
                    elif metric_name == 'website_clicks':
                        analytics_record.website_clicks = metric_value
                
                synced_records += 1
                
            except Exception as day_error:
                logger.error(f"Errore processamento giorno {day_data}: {day_error}")
                continue
        
        db.commit()
        
        logger.info(f"Sincronizzati {synced_records} record analytics per account {account_id}")
        return {
            "status": "success", 
            "account_id": account_id,
            "synced_records": synced_records
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        logger.error(f"Errore sync analytics account {account_id}: {error_msg}")
        return {"status": "error", "message": error_msg}
        
    finally:
        db.close()

@celery_app.task(name="sync_daily_analytics")
def sync_daily_analytics():
    """Task automatico per sincronizzare analytics giornalieri"""
    db = SessionLocal()
    results = []
    
    try:
        # Ottieni tutti gli account attivi business
        accounts = db.query(InstagramAccount).filter(
            InstagramAccount.is_active == True,
            InstagramAccount.is_business_account == True
        ).all()
        
        logger.info(f"Avvio sync analytics per {len(accounts)} account")
        
        for account in accounts:
            try:
                result = sync_account_analytics(account.id, days_back=1)
                results.append(result)
            except Exception as e:
                logger.error(f"Errore sync account {account.id}: {str(e)}")
                results.append({"status": "error", "account_id": account.id, "message": str(e)})
        
        success_count = len([r for r in results if r.get("status") == "success"])
        logger.info(f"Sync completato: {success_count}/{len(accounts)} account sincronizzati")
        
        return {
            "total_accounts": len(accounts),
            "successful": success_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Errore sync daily analytics: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()

@celery_app.task(bind=True, name="sync_post_analytics")
def sync_post_analytics(self, post_id: int):
    """Sincronizza analytics per post specifico"""
    db = SessionLocal()
    
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return {"status": "error", "message": "Post non trovato"}
        
        if not post.instagram_post_id:
            return {"status": "skipped", "message": "Post non pubblicato su Instagram"}
        
        account = post.account
        if not account or not account.is_active:
            return {"status": "error", "message": "Account non attivo"}
        
        # Ottieni insights post da Instagram
        # Usa versione sincrona per Celery
        insights = instagram_service.get_media_insights_sync(
            access_token=account.access_token,
            media_id=post.instagram_post_id
        )
        
        # Aggiorna metriche post
        for metric in insights.get('data', []):
            metric_name = metric.get('name', '')
            metric_values = metric.get('values', [])
            
            if metric_values:
                metric_value = metric_values[0].get('value', 0)
                
                if metric_name == 'impressions':
                    post.impressions = metric_value
                elif metric_name == 'reach':
                    post.reach = metric_value
                elif metric_name == 'likes':
                    post.like_count = metric_value
                elif metric_name == 'comments':
                    post.comment_count = metric_value
                elif metric_name == 'shares':
                    post.share_count = metric_value
                elif metric_name == 'saved':
                    post.saves_count = metric_value if hasattr(post, 'saves_count') else 0
        
        db.commit()
        
        logger.info(f"Analytics aggiornati per post {post_id}")
        return {"status": "success", "post_id": post_id}
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        logger.error(f"Errore sync analytics post {post_id}: {error_msg}")
        return {"status": "error", "message": error_msg}
        
    finally:
        db.close()

@celery_app.task(name="batch_sync_post_analytics")
def batch_sync_post_analytics(account_id: int = None, days_back: int = 7):
    """Sincronizza analytics per batch di post recenti"""
    db = SessionLocal()
    
    try:
        # Query post pubblicati negli ultimi N giorni
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        query = db.query(Post).filter(
            Post.status == PostStatus.PUBLISHED,
            Post.timestamp >= cutoff_date,
            Post.instagram_post_id.isnot(None)
        )
        
        if account_id:
            query = query.filter(Post.account_id == account_id)
        
        posts = query.all()
        
        logger.info(f"Avvio batch sync per {len(posts)} post")
        
        results = []
        for post in posts:
            try:
                result = sync_post_analytics(post.id)
                results.append(result)
            except Exception as e:
                logger.error(f"Errore sync post {post.id}: {str(e)}")
                results.append({"status": "error", "post_id": post.id, "message": str(e)})
        
        success_count = len([r for r in results if r.get("status") == "success"])
        logger.info(f"Batch sync completato: {success_count}/{len(posts)} post sincronizzati")
        
        return {
            "total_posts": len(posts),
            "successful": success_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Errore batch sync post analytics: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()

@celery_app.task(name="generate_analytics_report")
def generate_analytics_report(account_id: int, period_days: int = 30):
    """Genera report analytics per account"""
    db = SessionLocal()
    
    try:
        account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
        if not account:
            return {"status": "error", "message": "Account non trovato"}
        
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        
        # Ottieni analytics periodo
        analytics = db.query(Analytics).filter(
            Analytics.account_id == account_id,
            Analytics.date >= start_date,
            Analytics.date <= end_date
        ).order_by(Analytics.date).all()
        
        if not analytics:
            return {"status": "error", "message": "Nessun dato analytics trovato"}
        
        # Calcola metriche aggregate
        total_impressions = sum(a.total_impressions for a in analytics)
        total_reach = sum(a.total_reach for a in analytics)
        total_profile_views = sum(a.profile_views for a in analytics)
        
        # Crescita follower
        start_followers = analytics[0].followers_count if analytics else 0
        end_followers = analytics[-1].followers_count if analytics else 0
        follower_growth = end_followers - start_followers
        
        # Performance post nel periodo
        posts = db.query(Post).filter(
            Post.account_id == account_id,
            Post.status == PostStatus.PUBLISHED,
            Post.timestamp >= datetime.combine(start_date, datetime.min.time())
        ).all()
        
        total_likes = sum((p.like_count or 0) for p in posts)
        total_comments = sum((p.comment_count or 0) for p in posts)
        avg_engagement_rate = ((total_likes + total_comments) / total_reach * 100) if total_reach > 0 else 0
        
        report = {
            "account_id": account_id,
            "username": account.username,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": period_days
            },
            "metrics": {
                "total_impressions": total_impressions,
                "total_reach": total_reach,
                "total_profile_views": total_profile_views,
                "follower_growth": follower_growth,
                "posts_published": len(posts),
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_engagement_rate": round(avg_engagement_rate, 2)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Report generato per account {account_id}")
        return {"status": "success", "report": report}
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Errore generazione report account {account_id}: {error_msg}")
        return {"status": "error", "message": error_msg}
        
    finally:
        db.close()
