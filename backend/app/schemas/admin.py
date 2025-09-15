from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class AdminBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(AdminBase):
    password: Optional[str] = None

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminResponse(AdminBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
