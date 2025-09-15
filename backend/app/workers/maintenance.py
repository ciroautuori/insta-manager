from celery import current_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, or_
from datetime import datetime, timedelta
from loguru import logger

from app.core.config import settings
from app.models.instagram_account import InstagramAccount
from app.models.scheduled_post import ScheduledPost, ScheduleStatus
from app.models.post import Post, PostStatus
from app.models.media import Media, MediaStatus
from app.services.instagram_service import instagram_service
from app.workers.celery_app import celery_app

# Database session per workers
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task(name="refresh_instagram_tokens")
def refresh_instagram_tokens():
    """Rinnova automaticamente token Instagram in scadenza"""
    db = SessionLocal()
    results = []
    
    try:
        # Trova token in scadenza (prossimi 7 giorni)
        cutoff_time = datetime.utcnow() + timedelta(days=7)
        
        accounts = db.query(InstagramAccount).filter(
            InstagramAccount.is_active == True,
            InstagramAccount.token_expires_at.isnot(None),
            InstagramAccount.token_expires_at <= cutoff_time.timestamp()
        ).all()
        
        logger.info(f"Trovati {len(accounts)} account con token in scadenza")
        
        for account in accounts:
            try:
                # Rinnova token
                # Usa versione sincrona per Celery
                refresh_data = instagram_service.refresh_access_token_sync(account.access_token)
                
                new_token = refresh_data.get('access_token')
                expires_in = refresh_data.get('expires_in', 5184000)  # Default 60 giorni
                
                if new_token:
                    account.access_token = new_token
                    account.token_expires_at = datetime.utcnow().timestamp() + expires_in
                    
                    db.commit()
                    
                    logger.info(f"Token rinnovato per account {account.username}")
                    results.append({
                        "account_id": account.id,
                        "username": account.username,
                        "status": "success"
                    })
                else:
                    raise Exception("Token rinnovato non ricevuto")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Errore rinnovo token account {account.username}: {error_msg}")
                
                # Disattiva account se token non rinnovabile
                account.is_active = False
                db.commit()
                
                results.append({
                    "account_id": account.id,
                    "username": account.username,
                    "status": "error",
                    "message": error_msg
                })
        
        success_count = len([r for r in results if r.get("status") == "success"])
        logger.info(f"Refresh token completato: {success_count}/{len(accounts)} token rinnovati")
        
        return {
            "total_accounts": len(accounts),
            "successful": success_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Errore refresh token: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()

@celery_app.task(name="cleanup_failed_tasks")
def cleanup_failed_tasks():
    """Pulizia task falliti e post programmati orfani"""
    db = SessionLocal()
    
    try:
        cleanup_stats = {
            "cancelled_scheduled": 0,
            "reset_processing": 0,
            "deleted_old_failed": 0
        }
        
        # 1. Cancella post programmati molto vecchi falliti
        old_cutoff = datetime.utcnow() - timedelta(days=30)
        old_failed = db.query(ScheduledPost).filter(
            ScheduledPost.status == ScheduleStatus.FAILED,
            ScheduledPost.created_at <= old_cutoff
        ).all()
        
        for scheduled in old_failed:
            db.delete(scheduled)
            cleanup_stats["deleted_old_failed"] += 1
        
        # 2. Reset post bloccati in PROCESSING da molto tempo
        processing_cutoff = datetime.utcnow() - timedelta(hours=2)
        stuck_processing = db.query(ScheduledPost).filter(
            ScheduledPost.status == ScheduleStatus.PROCESSING,
            ScheduledPost.updated_at <= processing_cutoff
        ).all()
        
        for scheduled in stuck_processing:
            scheduled.status = ScheduleStatus.FAILED
            scheduled.last_error = "Task bloccato in processing - reset automatico"
            cleanup_stats["reset_processing"] += 1
        
        # 3. Cancella post programmati nel passato che non sono stati processati
        past_cutoff = datetime.utcnow() - timedelta(hours=1)
        past_pending = db.query(ScheduledPost).filter(
            ScheduledPost.status == ScheduleStatus.PENDING,
            ScheduledPost.scheduled_for <= past_cutoff
        ).all()
        
        for scheduled in past_pending:
            scheduled.status = ScheduleStatus.CANCELLED
            scheduled.last_error = "Post programmato nel passato - cancellato automaticamente"
            cleanup_stats["cancelled_scheduled"] += 1
        
        db.commit()
        
        logger.info(f"Cleanup completato: {cleanup_stats}")
        return {"status": "success", "cleanup_stats": cleanup_stats}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Errore cleanup tasks: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()

@celery_app.task(name="cleanup_orphaned_media")
def cleanup_orphaned_media():
    """Rimuove media files orfani non associati a post"""
    db = SessionLocal()
    
    try:
        import os
        
        # Trova media orfani (non associati a post)
        orphaned_media = db.query(Media).filter(
            Media.post_id.is_(None),
            Media.created_at <= datetime.utcnow() - timedelta(days=7)  # Orfani da almeno 7 giorni
        ).all()
        
        deleted_count = 0
        freed_space = 0
        
        for media in orphaned_media:
            try:
                # Elimina file fisico se esiste
                if os.path.exists(media.file_path):
                    file_size = os.path.getsize(media.file_path)
                    os.unlink(media.file_path)
                    freed_space += file_size
                
                # Elimina thumbnail se esiste
                if media.thumbnail_path and os.path.exists(media.thumbnail_path):
                    os.unlink(media.thumbnail_path)
                
                # Elimina record database
                db.delete(media)
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Errore eliminazione media {media.id}: {str(e)}")
                continue
        
        db.commit()
        
        logger.info(f"Cleanup media: {deleted_count} file eliminati, {freed_space} bytes liberati")
        return {
            "status": "success",
            "deleted_media": deleted_count,
            "freed_space_bytes": freed_space
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Errore cleanup media: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()

@celery_app.task(name="validate_account_tokens")
def validate_account_tokens():
    """Valida tutti i token Instagram attivi"""
    db = SessionLocal()
    results = []
    
    try:
        accounts = db.query(InstagramAccount).filter(InstagramAccount.is_active == True).all()
        
        for account in accounts:
            try:
                is_valid = instagram_service.validate_token(account.access_token)
                
                if not is_valid:
                    # Disattiva account con token non valido
                    account.is_active = False
                    db.commit()
                    
                    logger.warning(f"Token non valido per account {account.username} - account disattivato")
                    results.append({
                        "account_id": account.id,
                        "username": account.username,
                        "status": "invalid",
                        "action": "deactivated"
                    })
                else:
                    results.append({
                        "account_id": account.id,
                        "username": account.username,
                        "status": "valid"
                    })
                    
            except Exception as e:
                logger.error(f"Errore validazione token account {account.id}: {str(e)}")
                results.append({
                    "account_id": account.id,
                    "username": account.username if account.username else "unknown",
                    "status": "error",
                    "message": str(e)
                })
        
        valid_count = len([r for r in results if r.get("status") == "valid"])
        invalid_count = len([r for r in results if r.get("status") == "invalid"])
        
        logger.info(f"Validazione token: {valid_count} validi, {invalid_count} non validi")
        
        return {
            "total_accounts": len(accounts),
            "valid_tokens": valid_count,
            "invalid_tokens": invalid_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Errore validazione account tokens: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()

@celery_app.task(name="sync_account_profiles")
def sync_account_profiles():
    """Sincronizza profili account Instagram (follower, following, etc.)"""
    db = SessionLocal()
    results = []
    
    try:
        accounts = db.query(InstagramAccount).filter(InstagramAccount.is_active == True).all()
        
        for account in accounts:
            try:
                # Usa versione sincrona per Celery
                updated_account = instagram_service.sync_account_data_sync(db, account)
                
                results.append({
                    "account_id": account.id,
                    "username": account.username,
                    "status": "success",
                    "followers_count": updated_account.followers_count,
                    "following_count": updated_account.following_count,
                    "posts_count": updated_account.posts_count
                })
                
            except Exception as e:
                logger.error(f"Errore sync profile account {account.id}: {str(e)}")
                results.append({
                    "account_id": account.id,
                    "username": account.username,
                    "status": "error",
                    "message": str(e)
                })
        
        success_count = len([r for r in results if r.get("status") == "success"])
        logger.info(f"Sync profili: {success_count}/{len(accounts)} account sincronizzati")
        
        return {
            "total_accounts": len(accounts),
            "successful": success_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Errore sync account profiles: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()

@celery_app.task(name="database_maintenance")
def database_maintenance():
    """Manutenzione generale database"""
    db = SessionLocal()
    
    try:
        maintenance_stats = {
            "analyzed_tables": 0,
            "cleaned_logs": 0,
            "optimized": True
        }
        
        # Pulizia log vecchi (se presenti tabelle log)
        # Questo dipende dalla struttura specifica del database
        
        # Aggiorna statistiche tabelle PostgreSQL
        try:
            db.execute("ANALYZE;")
            maintenance_stats["analyzed_tables"] = 1
        except Exception as e:
            logger.warning(f"Impossibile eseguire ANALYZE: {str(e)}")
        
        db.commit()
        
        logger.info("Database maintenance completato")
        return {"status": "success", "stats": maintenance_stats}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Errore database maintenance: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()

@celery_app.task(name="health_check_system")
def health_check_system():
    """Health check generale sistema"""
    db = SessionLocal()
    
    try:
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "database": "unknown",
            "redis": "unknown",
            "instagram_api": "unknown",
            "storage": "unknown"
        }
        
        # Test database
        try:
            db.execute("SELECT 1")
            health_data["database"] = "healthy"
        except Exception as e:
            health_data["database"] = f"error: {str(e)}"
        
        # Test Redis
        try:
            import redis
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            health_data["redis"] = "healthy"
        except Exception as e:
            health_data["redis"] = f"error: {str(e)}"
        
        # Test storage
        try:
            import os
            if os.path.exists(settings.MEDIA_STORAGE_PATH) and os.access(settings.MEDIA_STORAGE_PATH, os.W_OK):
                health_data["storage"] = "healthy"
            else:
                health_data["storage"] = "error: storage path not writable"
        except Exception as e:
            health_data["storage"] = f"error: {str(e)}"
        
        # Test Instagram API con account casuale
        try:
            sample_account = db.query(InstagramAccount).filter(InstagramAccount.is_active == True).first()
            if sample_account:
                is_valid = instagram_service.validate_token(sample_account.access_token)
                health_data["instagram_api"] = "healthy" if is_valid else "error: token validation failed"
            else:
                health_data["instagram_api"] = "no active accounts"
        except Exception as e:
            health_data["instagram_api"] = f"error: {str(e)}"
        
        return {"status": "success", "health": health_data}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()
