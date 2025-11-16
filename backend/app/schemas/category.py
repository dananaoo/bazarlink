"""
Category schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str
    description: Optional[str] = None
    display_order: int = 0


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    supplier_id: int


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryInDB(CategoryBase):
    """Category schema in database"""
    id: int
    supplier_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Category(CategoryInDB):
    """Category schema for API responses"""
    pass

