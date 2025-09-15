from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.schemas.admin import AdminResponse, AdminUpdate

router = APIRouter()

@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ottieni informazioni admin corrente"""
    admin = db.query(Admin).filter(Admin.email == current_admin["email"]).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin non trovato"
        )
    return admin

@router.get("/", response_model=List[AdminResponse])
async def list_admins(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista tutti gli admin (solo superuser)"""
    admin = db.query(Admin).filter(Admin.email == current_admin["email"]).first()
    if not admin or not admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato: richiesti privilegi superuser"
        )
    
    admins = db.query(Admin).all()
    return admins

@router.put("/me", response_model=AdminResponse)
async def update_current_admin(
    admin_update: AdminUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Aggiorna profilo admin corrente"""
    admin = db.query(Admin).filter(Admin.email == current_admin["email"]).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin non trovato"
        )
    
    # Aggiorna campi se forniti
    if admin_update.full_name is not None:
        admin.full_name = admin_update.full_name
    
    if admin_update.password is not None:
        from app.core.security import get_password_hash
        admin.hashed_password = get_password_hash(admin_update.password)
    
    db.commit()
    db.refresh(admin)
    return admin

@router.delete("/{admin_id}")
async def delete_admin(
    admin_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Elimina admin (solo superuser)"""
    admin = db.query(Admin).filter(Admin.email == current_admin["email"]).first()
    if not admin or not admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso negato: richiesti privilegi superuser"
        )
    
    admin_to_delete = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin non trovato"
        )
    
    if admin_to_delete.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non puoi eliminare il tuo account"
        )
    
    db.delete(admin_to_delete)
    db.commit()
    
    return {"message": "Admin eliminato con successo"}
