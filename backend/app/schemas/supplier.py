"""
Supplier schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.supplier import VerificationStatus


class SupplierBase(BaseModel):
    """Base supplier schema"""
    company_name: str
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "KZ"
    description: Optional[str] = None
    website: Optional[str] = None


class SupplierCreate(SupplierBase):
    """Schema for creating a supplier"""
    pass


class SupplierUpdate(BaseModel):
    """Schema for updating a supplier"""
    company_name: Optional[str] = None
    legal_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierInDB(SupplierBase):
    """Supplier schema in database"""
    id: int
    verification_status: VerificationStatus
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Supplier(SupplierInDB):
    """Supplier schema for API responses"""
    pass

