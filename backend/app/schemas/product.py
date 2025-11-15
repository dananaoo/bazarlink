"""
Product schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.product import ProductUnit


class ProductBase(BaseModel):
    """Base product schema"""
    name: str
    description: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    price: Decimal
    discount_price: Optional[Decimal] = None
    currency: str = "KZT"
    stock_quantity: Decimal = Decimal("0")
    unit: ProductUnit = ProductUnit.KILOGRAM
    min_order_quantity: Decimal = Decimal("1")
    delivery_available: bool = True
    pickup_available: bool = True
    lead_time_days: int = 1


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    supplier_id: int


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    price: Optional[Decimal] = None
    discount_price: Optional[Decimal] = None
    stock_quantity: Optional[Decimal] = None
    unit: Optional[ProductUnit] = None
    min_order_quantity: Optional[Decimal] = None
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None
    delivery_available: Optional[bool] = None
    pickup_available: Optional[bool] = None
    lead_time_days: Optional[int] = None


class ProductInDB(ProductBase):
    """Product schema in database"""
    id: int
    supplier_id: int
    is_available: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Product(ProductInDB):
    """Product schema for API responses"""
    pass

