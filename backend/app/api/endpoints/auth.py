from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.models.admin import Admin
from app.schemas.admin import AdminLogin, Token, AdminCreate, AdminResponse

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login admin e rilascio JWT token"""
    
    # Verifica credenziali admin
    admin = db.query(Admin).filter(Admin.email == form_data.username).first()
    
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password incorretti"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disattivato"
        )
    
    # Aggiorna ultimo login
    from datetime import datetime
    admin.last_login = datetime.utcnow()
    db.commit()
    
    # Crea access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/register", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    """Registrazione nuovo admin (solo per setup iniziale)"""
    
    # Verifica se esiste già un admin
    existing_admin = db.query(Admin).filter(Admin.email == admin_data.email).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin già esistente con questa email"
        )
    
    # Crea nuovo admin
    hashed_password = get_password_hash(admin_data.password)
    new_admin = Admin(
        email=admin_data.email,
        hashed_password=hashed_password,
        full_name=admin_data.full_name,
        is_active=True,
        is_superuser=True  # Il primo admin è sempre superuser
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return new_admin
