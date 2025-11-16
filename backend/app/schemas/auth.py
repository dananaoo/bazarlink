"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.supplier import SupplierCreate


class OwnerRegistration(BaseModel):
    """Schema for owner registration"""
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    language: str = "en"
    supplier: SupplierCreate

