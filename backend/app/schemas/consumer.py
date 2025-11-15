"""
Consumer schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ConsumerBase(BaseModel):
    """Base consumer schema"""
    business_name: str
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "KZ"
    business_type: Optional[str] = None
    description: Optional[str] = None


class ConsumerCreate(ConsumerBase):
    """Schema for creating a consumer"""
    pass


class ConsumerUpdate(BaseModel):
    """Schema for updating a consumer"""
    business_name: Optional[str] = None
    legal_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    business_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ConsumerInDB(ConsumerBase):
    """Consumer schema in database"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Consumer(ConsumerInDB):
    """Consumer schema for API responses"""
    pass

