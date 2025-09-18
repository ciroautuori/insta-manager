from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.scheduled_post import ScheduledPost, ScheduleStatus
from app.models.instagram_account import InstagramAccount
from app.schemas.scheduled_post import (
    ScheduledPostCreate, 
    ScheduledPostResponse, 
    ScheduledPostUpdate,
    ScheduledPostStats
)

router = APIRouter()

@router.post("/", response_model=ScheduledPostResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_post(
    scheduled_data: ScheduledPostCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crea nuovo post programmato"""
    
    # Verifica account exists
    account = db.query(InstagramAccount).filter(InstagramAccount.id == scheduled_data.account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    # Verifica che scheduled_for sia nel futuro
    if scheduled_data.scheduled_for <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data pianificazione deve essere nel futuro"
        )
    
    # Crea scheduled post
    new_scheduled = ScheduledPost(
        account_id=scheduled_data.account_id,
        caption=scheduled_data.caption,
        hashtags=scheduled_data.hashtags,
        post_type=scheduled_data.post_type,
        media_files=scheduled_data.media_files,
        scheduled_for=scheduled_data.scheduled_for,
        location_id=scheduled_data.location_id,
        location_name=scheduled_data.location_name
    )
    
    db.add(new_scheduled)
    db.commit()
    db.refresh(new_scheduled)
    
    # Programma task Celery per pubblicazione
    from app.workers.publisher import schedule_post_publication
    task = schedule_post_publication.apply_async(
        args=[new_scheduled.id],
        eta=scheduled_data.scheduled_for
    )
    
    # Salva task ID
    new_scheduled.celery_task_id = task.id
    db.commit()
    
    return new_scheduled

@router.get("/", response_model=List[ScheduledPostResponse])
async def list_scheduled_posts(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    account_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Lista post programmati"""
    query = db.query(ScheduledPost)
    
    if account_id:
        query = query.filter(ScheduledPost.account_id == account_id)
    
    if status_filter:
        try:
            status_enum = ScheduleStatus(status_filter)
            query = query.filter(ScheduledPost.status == status_enum)
        except ValueError:
            # stato non valido: ignora filtro
            pass
    
    scheduled_posts = query.order_by(ScheduledPost.scheduled_for.asc()).offset(offset).limit(limit).all()
    return scheduled_posts

@router.get("/{scheduled_id}", response_model=ScheduledPostResponse)
async def get_scheduled_post(
    scheduled_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ottieni dettagli post programmato"""
    scheduled = db.query(ScheduledPost).filter(ScheduledPost.id == scheduled_id).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post programmato non trovato"
        )
    
    return scheduled

@router.put("/{scheduled_id}", response_model=ScheduledPostResponse)
async def update_scheduled_post(
    scheduled_id: int,
    update_data: ScheduledPostUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Aggiorna post programmato"""
    scheduled = db.query(ScheduledPost).filter(ScheduledPost.id == scheduled_id).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post programmato non trovato"
        )
    
    if scheduled.status not in [ScheduleStatus.PENDING, ScheduleStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Puoi modificare solo post pending o failed"
        )
    
    # Aggiorna campi
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(scheduled, field, value)
    
    # Se cambia scheduled_for, aggiorna task Celery
    if 'scheduled_for' in update_dict:
        if update_dict['scheduled_for'] <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data pianificazione deve essere nel futuro"
            )
        
        # Cancella task esistente se present
        if scheduled.celery_task_id:
            from app.workers.publisher import cancel_scheduled_task
            cancel_scheduled_task(scheduled.celery_task_id)
        
        # Crea nuovo task
        from app.workers.publisher import schedule_post_publication
        task = schedule_post_publication.apply_async(
            args=[scheduled.id],
            eta=update_dict['scheduled_for']
        )
        scheduled.celery_task_id = task.id
    
    db.commit()
    db.refresh(scheduled)
    return scheduled

@router.delete("/{scheduled_id}")
async def cancel_scheduled_post(
    scheduled_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Cancella post programmato"""
    scheduled = db.query(ScheduledPost).filter(ScheduledPost.id == scheduled_id).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post programmato non trovato"
        )
    
    if scheduled.status == ScheduleStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non puoi cancellare un post già pubblicato"
        )
    
    # Cancella task Celery
    if scheduled.celery_task_id:
        from app.workers.publisher import cancel_scheduled_task
        cancel_scheduled_task(scheduled.celery_task_id)
    
    # Aggiorna status o elimina
    scheduled.status = ScheduleStatus.CANCELLED
    db.commit()
    
    return {"message": "Post programmato cancellato"}

@router.post("/{scheduled_id}/execute")
async def execute_scheduled_post_now(
    scheduled_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Esegui immediatamente post programmato"""
    scheduled = db.query(ScheduledPost).filter(ScheduledPost.id == scheduled_id).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post programmato non trovato"
        )
    
    if scheduled.status != ScheduleStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Puoi eseguire solo post pending"
        )
    
    # Cancella task programmato
    if scheduled.celery_task_id:
        from app.workers.publisher import cancel_scheduled_task
        cancel_scheduled_task(scheduled.celery_task_id)

    # Esegui ora tramite Celery
    from app.workers.publisher import publish_scheduled_post
    task = publish_scheduled_post.apply_async(args=[scheduled.id])
    scheduled.celery_task_id = task.id
    
    scheduled.status = ScheduleStatus.PROCESSING
    db.commit()
    
    return {"message": "Post in corso di pubblicazione", "task_id": task.id}

@router.get("/stats/overview", response_model=ScheduledPostStats)
async def get_scheduled_stats(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    account_id: Optional[int] = None
):
    """Statistiche post programmati"""
    query = db.query(ScheduledPost)
    
    if account_id:
        query = query.filter(ScheduledPost.account_id == account_id)
    
    all_scheduled = query.all()
    
    stats = ScheduledPostStats(
        total_scheduled=len(all_scheduled),
        pending=len([s for s in all_scheduled if s.status == ScheduleStatus.PENDING]),
        published=len([s for s in all_scheduled if s.status == ScheduleStatus.PUBLISHED]),
        failed=len([s for s in all_scheduled if s.status == ScheduleStatus.FAILED]),
        cancelled=len([s for s in all_scheduled if s.status == ScheduleStatus.CANCELLED])
    )
    
    return stats

@router.get("/calendar/{year}/{month}")
async def get_calendar_scheduled_posts(
    year: int,
    month: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    account_id: Optional[int] = None
):
    """Ottieni post programmati per calendario mensile"""
    
    # Calcola range date per il mese
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    query = db.query(ScheduledPost).filter(
        ScheduledPost.scheduled_for >= start_date,
        ScheduledPost.scheduled_for <= end_date
    )
    
    if account_id:
        query = query.filter(ScheduledPost.account_id == account_id)
    
    scheduled_posts = query.order_by(ScheduledPost.scheduled_for).all()
    
    # Raggruppa per giorno
    calendar_data = {}
    for post in scheduled_posts:
        day = post.scheduled_for.day
        if day not in calendar_data:
            calendar_data[day] = []
        
        calendar_data[day].append({
            "id": post.id,
            "time": post.scheduled_for.strftime("%H:%M"),
            "caption": post.caption[:50] + "..." if post.caption and len(post.caption) > 50 else post.caption,
            "status": post.status,
            "account_username": post.account.username
        })
    
    return calendar_data
