from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_admin
from app.core.config import settings
from app.models.post import Post, PostStatus, PostType
from app.models.instagram_account import InstagramAccount
from app.models.media import Media, MediaStatus
from app.schemas.post import PostCreate, PostResponse, PostUpdate, PostStats, PostAnalytics
from app.services.instagram_service import instagram_service

router = APIRouter()


def _serialize_post(post: Post) -> PostResponse:
    """Serializza un Post SQLAlchemy nel PostResponse schema, mappando i nomi campo."""
    return PostResponse(
        id=post.id,
        account_id=post.account_id,
        caption=post.caption,
        hashtags=None,  # non presente nel modello
        post_type=post.post_type,
        location_id=None,  # non presente nel modello
        location_name=None,  # non presente nel modello
        instagram_post_id=post.instagram_post_id,
        status=post.status,
        likes_count=post.like_count or 0,
        comments_count=post.comment_count or 0,
        shares_count=post.share_count or 0,
        impressions=post.impressions or 0,
        reach=post.reach or 0,
        published_at=post.timestamp,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crea nuovo post"""
    # Verifica che l'account esista
    account = db.query(InstagramAccount).filter(InstagramAccount.id == post_data.account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )

    # Crea post (ignora campi non presenti nel modello)
    new_post = Post(
        account_id=post_data.account_id,
        caption=post_data.caption,
        post_type=post_data.post_type,
        status=PostStatus.DRAFT,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # Associa media se forniti
    if post_data.media_files:
        for media_id in post_data.media_files:
            media = db.query(Media).filter(Media.id == media_id).first()
            if media:
                media.post_id = new_post.id
        db.commit()

    return _serialize_post(new_post)

@router.get("/", response_model=List[PostResponse])
async def list_posts(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    account_id: Optional[int] = Query(None, description="Filtra per account ID"),
    status_filter: Optional[str] = Query(None, description="Filtra per status"),
    limit: int = Query(50, le=100, description="Numero massimo post"),
    offset: int = Query(0, description="Offset per paginazione")
):
    """Lista posts con filtri"""
    query = db.query(Post)
    
    if account_id:
        query = query.filter(Post.account_id == account_id)
    
    if status_filter:
        try:
            status_enum = PostStatus(status_filter)
            query = query.filter(Post.status == status_enum)
        except ValueError:
            # status non valido, ignora il filtro
            pass
    
    posts = query.order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
    return [_serialize_post(p) for p in posts]

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ottieni dettagli post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trovato"
        )
    
    return _serialize_post(post)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Aggiorna post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trovato"
        )
    
    # Aggiorna campi consentiti
    update_data = post_update.dict(exclude_unset=True)
    allowed_fields = {"caption", "status", "location_id", "location_name", "post_type"}
    for field, value in update_data.items():
        if field == "status" and value is not None:
            # assicurati che sia un Enum PostStatus
            if isinstance(value, str):
                try:
                    value = PostStatus(value)
                except ValueError:
                    continue
        if field == "post_type" and value is not None and isinstance(value, str):
            try:
                value = PostType(value)
            except ValueError:
                continue
        if field in {"location_id", "location_name"}:
            # ignorati: non esistono nel modello
            continue
        if field in allowed_fields and hasattr(post, field):
            setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return _serialize_post(post)

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Elimina post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trovato"
        )
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post eliminato con successo"}

@router.post("/{post_id}/publish")
async def publish_post(
    post_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Pubblica post su Instagram"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trovato"
        )
    
    if post.status != PostStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo i post in bozza possono essere pubblicati"
        )
    
    try:
        # Prepara media URLs per Instagram
        media_urls = []
        for media in post.media:
            if media.status == MediaStatus.READY:
                # Genera URL completo usando filename e base URL pubblica
                base = settings.PUBLIC_MEDIA_BASE_URL.rstrip('/')
                media_urls.append(f"{base}/{media.filename}")
        
        if not media_urls:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post deve avere almeno un media pronto"
            )
        
        # Pubblica su Instagram
        instagram_post_id = await instagram_service.create_post(
            access_token=post.account.access_token,
            media_urls=media_urls,
            caption=post.caption,
            location_id=None
        )
        
        # Aggiorna post
        post.instagram_post_id = instagram_post_id
        post.status = PostStatus.PUBLISHED
        post.timestamp = datetime.utcnow()
        
        db.commit()
        db.refresh(post)
        
        return {"message": "Post pubblicato con successo", "instagram_post_id": instagram_post_id}
        
    except Exception as e:
        post.status = PostStatus.ARCHIVED if "rate limit" in str(e).lower() else PostStatus.DRAFT
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore pubblicazione: {str(e)}"
        )

@router.get("/{post_id}/analytics", response_model=PostAnalytics)
async def get_post_analytics(
    post_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ottieni analytics post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trovato"
        )
    
    if not post.instagram_post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post non ancora pubblicato su Instagram"
        )
    
    try:
        # Ottieni insights da Instagram
        insights = await instagram_service.get_media_insights(
            access_token=post.account.access_token,
            media_id=post.instagram_post_id
        )
        
        # Aggiorna metriche post
        for metric in insights.get('data', []):
            metric_name = metric['name']
            metric_value = metric['values'][0]['value']
            
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
        
        # Calcola engagement rate
        engagement_rate = 0.0
        if (post.reach or 0) > 0:
            total_engagement = (post.like_count or 0) + (post.comment_count or 0) + (post.share_count or 0)
            engagement_rate = (total_engagement / post.reach) * 100
        
        db.commit()
        
        return PostAnalytics(
            post_id=post.id,
            likes_count=post.like_count or 0,
            comments_count=post.comment_count or 0,
            shares_count=post.share_count or 0,
            impressions=post.impressions or 0,
            reach=post.reach or 0,
            engagement_rate=round(engagement_rate, 2),
            posted_at=post.timestamp
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore ottenimento analytics: {str(e)}"
        )

@router.get("/stats/overview", response_model=PostStats)
async def get_posts_stats(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    account_id: Optional[int] = Query(None, description="Filtra per account ID")
):
    """Ottieni statistiche generali posts"""
    query = db.query(Post)
    
    if account_id:
        query = query.filter(Post.account_id == account_id)
    
    posts = query.all()
    
    total_posts = len(posts)
    published_posts = len([p for p in posts if p.status == PostStatus.PUBLISHED])
    draft_posts = len([p for p in posts if p.status == PostStatus.DRAFT])
    failed_posts = len([p for p in posts if p.status == PostStatus.ARCHIVED])
    
    total_likes = sum((p.like_count or 0) for p in posts)
    total_comments = sum((p.comment_count or 0) for p in posts)
    total_reach = sum((p.reach or 0) for p in posts)
    
    engagement_rate = 0.0
    if total_reach > 0:
        engagement_rate = ((total_likes + total_comments) / total_reach) * 100
    
    return PostStats(
        total_posts=total_posts,
        published_posts=published_posts,
        draft_posts=draft_posts,
        failed_posts=failed_posts,
        total_likes=total_likes,
        total_comments=total_comments,
        engagement_rate=round(engagement_rate, 2)
    )
