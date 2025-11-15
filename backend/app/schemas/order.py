"""
Order schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""
    product_id: int
    quantity: Decimal


class OrderItemBase(BaseModel):
    """Base order item schema"""
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal


class OrderItemInDB(OrderItemBase):
    """Order item schema in database"""
    id: int
    order_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrderItem(OrderItemInDB):
    """Order item schema for API responses"""
    pass


class OrderBase(BaseModel):
    """Base order schema"""
    supplier_id: int
    consumer_id: int
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Schema for creating an order"""
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatus] = None
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class OrderInDB(OrderBase):
    """Order schema in database"""
    id: int
    order_number: str
    status: OrderStatus
    subtotal: Decimal
    total: Decimal
    currency: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Order(OrderInDB):
    """Order schema for API responses"""
    items: List[OrderItem] = []

