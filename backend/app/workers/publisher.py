from celery import current_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import traceback
from loguru import logger

from app.core.config import settings
from app.models.scheduled_post import ScheduledPost, ScheduleStatus
from app.models.post import Post, PostStatus, PostType
from app.models.media import Media
from app.models.instagram_account import InstagramAccount
from app.services.instagram_service import instagram_service
from app.workers.celery_app import celery_app

# Database session per workers
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task(bind=True, name="publish_scheduled_post")
def publish_scheduled_post(self, scheduled_post_id: int):
    """Task per pubblicare post programmato"""
    db = SessionLocal()
    
    try:
        # Ottieni scheduled post
        scheduled = db.query(ScheduledPost).filter(ScheduledPost.id == scheduled_post_id).first()
        if not scheduled:
            logger.error(f"Scheduled post {scheduled_post_id} non trovato")
            return {"status": "error", "message": "Scheduled post non trovato"}
        
        # Verifica stato
        if scheduled.status != ScheduleStatus.PENDING:
            logger.warning(f"Scheduled post {scheduled_post_id} non è in stato PENDING")
            return {"status": "skipped", "message": "Post non in stato pending"}
        
        # Aggiorna stato a PROCESSING
        scheduled.status = ScheduleStatus.PROCESSING
        db.commit()
        
        # Ottieni account
        account = db.query(InstagramAccount).filter(InstagramAccount.id == scheduled.account_id).first()
        if not account or not account.is_active:
            raise Exception("Account Instagram non attivo")
        
        # Verifica token
        if not instagram_service.validate_token(account.access_token):
            raise Exception("Token Instagram non valido")
        
        # Prepara media URLs se presenti
        media_urls = []
        if scheduled.media_files:
            for media_path in scheduled.media_files:
                # Genera URL completo per il media
                media_url = f"https://yourdomain.com/media/{media_path}"
                media_urls.append(media_url)
        
        # Pubblica su Instagram
        instagram_post_id = None
        if media_urls:
            # Celery non supporta await direttamente, usa sync version
            instagram_post_id = instagram_service.create_post_sync(
                access_token=account.access_token,
                media_urls=media_urls,
                caption=scheduled.caption,
                location_id=scheduled.location_id
            )
        else:
            # Se non ci sono media, non si può pubblicare
            raise Exception("Post deve contenere almeno un media")
        
        # Crea record post pubblicato
        new_post = Post(
            account_id=scheduled.account_id,
            instagram_post_id=instagram_post_id,
            caption=scheduled.caption,
            hashtags=scheduled.hashtags,
            post_type=PostType(scheduled.post_type),
            status=PostStatus.PUBLISHED,
            published_at=datetime.utcnow(),
            location_id=scheduled.location_id,
            location_name=scheduled.location_name
        )
        
        db.add(new_post)
        db.flush()  # Per ottenere l'ID
        
        # Aggiorna scheduled post
        scheduled.status = ScheduleStatus.PUBLISHED
        scheduled.published_post_id = new_post.id
        scheduled.instagram_post_id = instagram_post_id
        scheduled.published_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Post programmato {scheduled_post_id} pubblicato con successo: {instagram_post_id}")
        
        return {
            "status": "success",
            "scheduled_post_id": scheduled_post_id,
            "instagram_post_id": instagram_post_id,
            "published_post_id": new_post.id
        }
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        logger.error(f"Errore pubblicazione post {scheduled_post_id}: {error_msg}")
        
        # Aggiorna scheduled post con errore
        try:
            scheduled = db.query(ScheduledPost).filter(ScheduledPost.id == scheduled_post_id).first()
            if scheduled:
                scheduled.status = ScheduleStatus.FAILED
                scheduled.last_error = error_msg
                scheduled.retry_count += 1
                
                # Riprova se non ha superato max retry
                if scheduled.retry_count < scheduled.max_retries:
                    logger.info(f"Riprogrammazione retry {scheduled.retry_count} per post {scheduled_post_id}")
                    # Riprova fra 5 minuti
                    retry_time = datetime.utcnow().timestamp() + (5 * 60)
                    self.retry(countdown=300, max_retries=scheduled.max_retries)
                
                db.commit()
        except Exception as retry_error:
            logger.error(f"Errore aggiornamento stato retry: {retry_error}")
        
        return {"status": "error", "message": error_msg}
        
    finally:
        db.close()

@celery_app.task(name="schedule_post_publication")
def schedule_post_publication(scheduled_post_id: int):
    """Task wrapper per schedulare pubblicazione"""
    return publish_scheduled_post.delay(scheduled_post_id)

@celery_app.task(name="cancel_scheduled_task")
def cancel_scheduled_task(task_id: str):
    """Cancella task programmato"""
    try:
        current_app.control.revoke(task_id, terminate=True)
        logger.info(f"Task {task_id} cancellato")
        return {"status": "success", "task_id": task_id}
    except Exception as e:
        logger.error(f"Errore cancellazione task {task_id}: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name="bulk_publish_posts")
def bulk_publish_posts(self, scheduled_post_ids: list):
    """Pubblica multipli post in batch"""
    results = []
    
    for post_id in scheduled_post_ids:
        try:
            result = publish_scheduled_post(post_id)
            results.append({"post_id": post_id, "result": result})
        except Exception as e:
            results.append({"post_id": post_id, "error": str(e)})
    
    return {
        "total_processed": len(scheduled_post_ids),
        "results": results
    }

@celery_app.task(name="republish_failed_post")
def republish_failed_post(scheduled_post_id: int):
    """Ripubblica post fallito"""
    db = SessionLocal()
    
    try:
        scheduled = db.query(ScheduledPost).filter(ScheduledPost.id == scheduled_post_id).first()
        if not scheduled:
            return {"status": "error", "message": "Post non trovato"}
        
        if scheduled.status != ScheduleStatus.FAILED:
            return {"status": "error", "message": "Post non è in stato failed"}
        
        # Reset stato e contatori
        scheduled.status = ScheduleStatus.PENDING
        scheduled.retry_count = 0
        scheduled.last_error = None
        
        db.commit()
        
        # Ripubblica immediatamente
        return publish_scheduled_post(scheduled_post_id)
        
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
