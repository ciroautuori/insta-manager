from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import secrets
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.instagram_account import InstagramAccount
from app.schemas.instagram_account import (
    InstagramAccountResponse, 
    InstagramAccountCreate, 
    InstagramAccountUpdate,
    InstagramAuthURL,
    InstagramTokenExchange,
    InstagramAccountStats
)
from app.services.instagram_service import instagram_service

router = APIRouter()

@router.get("/auth/url", response_model=InstagramAuthURL)
async def get_instagram_auth_url(current_admin: dict = Depends(get_current_admin)):
    """Genera URL per autorizzazione Instagram"""
    state = secrets.token_urlsafe(32)
    auth_url = instagram_service.get_authorization_url(state)
    
    return InstagramAuthURL(auth_url=auth_url, state=state)

@router.post("/auth/callback")
async def instagram_auth_callback(
    token_data: InstagramTokenExchange,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Callback per completare autorizzazione Instagram"""
    try:
        # Scambia codice con token
        token_response = await instagram_service.exchange_code_for_token(token_data.code)
        access_token = token_response['access_token']
        
        # Ottieni long-lived token
        long_lived_response = await instagram_service.get_long_lived_token(access_token)
        long_lived_token = long_lived_response['access_token']
        expires_in = long_lived_response.get('expires_in', 3600)
        
        # Ottieni dati profilo
        profile_data = await instagram_service.get_user_profile(long_lived_token)
        
        # Verifica se account già esiste
        existing_account = db.query(InstagramAccount).filter(
            InstagramAccount.instagram_user_id == profile_data['id']
        ).first()
        
        if existing_account:
            # Aggiorna token esistente
            existing_account.access_token = long_lived_token
            existing_account.token_expires_at = datetime.utcnow().timestamp() + expires_in
            existing_account.is_active = True
            existing_account.last_sync = datetime.utcnow()
            db.commit()
            db.refresh(existing_account)
            return {"message": "Account Instagram aggiornato", "account": existing_account}
        
        # Crea nuovo account
        new_account = InstagramAccount(
            instagram_user_id=profile_data['id'],
            username=profile_data['username'],
            access_token=long_lived_token,
            token_expires_at=datetime.utcnow().timestamp() + expires_in,
            followers_count=profile_data.get('followers_count', 0),
            following_count=profile_data.get('follows_count', 0),
            posts_count=profile_data.get('media_count', 0),
            is_business_account=profile_data.get('account_type') == 'BUSINESS',
            permissions=['instagram_basic', 'instagram_content_publish', 'instagram_manage_insights']
        )
        
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        
        return {"message": "Account Instagram connesso con successo", "account": new_account}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore connessione Instagram: {str(e)}"
        )

@router.get("/accounts", response_model=List[InstagramAccountResponse])
async def list_instagram_accounts(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    active_only: bool = Query(True, description="Solo account attivi")
):
    """Lista account Instagram connessi"""
    query = db.query(InstagramAccount)
    
    if active_only:
        query = query.filter(InstagramAccount.is_active == True)
    
    accounts = query.order_by(InstagramAccount.created_at.desc()).all()
    return accounts

@router.get("/accounts/{account_id}", response_model=InstagramAccountResponse)
async def get_instagram_account(
    account_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ottieni dettagli account Instagram"""
    account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    return account

@router.put("/accounts/{account_id}", response_model=InstagramAccountResponse)
async def update_instagram_account(
    account_id: int,
    account_update: InstagramAccountUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Aggiorna account Instagram"""
    account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    # Aggiorna campi se forniti
    update_data = account_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    return account

@router.post("/accounts/{account_id}/sync")
async def sync_instagram_account(
    account_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Sincronizza dati account con Instagram"""
    account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    try:
        updated_account = await instagram_service.sync_account_data(db, account)
        return {"message": "Account sincronizzato", "account": updated_account}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore sincronizzazione: {str(e)}"
        )

@router.delete("/accounts/{account_id}")
async def delete_instagram_account(
    account_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Disconnetti account Instagram"""
    account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    # Soft delete - disattiva invece di eliminare
    account.is_active = False
    account.access_token = ""  # Rimuovi token per sicurezza
    
    db.commit()
    
    return {"message": "Account Instagram disconnesso"}

@router.get("/accounts/{account_id}/stats", response_model=InstagramAccountStats)
async def get_account_stats(
    account_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ottieni statistiche account"""
    account = db.query(InstagramAccount).filter(InstagramAccount.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Instagram non trovato"
        )
    
    # Calcola engagement rate (approssimativo)
    total_posts = len(account.posts)
    total_engagement = sum(post.likes_count + post.comments_count for post in account.posts)
    engagement_rate = (total_engagement / (account.followers_count * total_posts)) * 100 if account.followers_count > 0 and total_posts > 0 else 0.0
    
    # Ultimo post
    last_post_date = None
    if account.posts:
        last_post = max(account.posts, key=lambda p: p.created_at)
        last_post_date = last_post.published_at or last_post.created_at
    
    return InstagramAccountStats(
        account_id=account.id,
        username=account.username,
        followers_count=account.followers_count,
        posts_count=len(account.posts),
        engagement_rate=round(engagement_rate, 2),
        last_post_date=last_post_date
    )
