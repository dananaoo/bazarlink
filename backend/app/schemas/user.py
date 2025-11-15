"""
User schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    language: str = "en"


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str
    role: UserRole


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """User schema in database"""
    id: int
    role: UserRole
    is_active: bool
    supplier_id: Optional[int] = None
    consumer_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        # Pydantic v2 compatibility
        use_enum_values = True


class User(UserInDB):
    """User schema for API responses"""
    pass


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[int] = None

