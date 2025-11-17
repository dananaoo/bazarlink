"""
Message schemas for chat functionality
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    """Base message schema"""
    content: str
    message_type: str = "text"
    attachment_url: Optional[str] = None
    attachment_type: Optional[str] = None
    product_id: Optional[int] = None
    order_id: Optional[int] = None


class MessageCreate(MessageBase):
    """Schema for creating a message"""
    link_id: int
    receiver_id: Optional[int] = None  # If None, message is to supplier staff


class MessageUpdate(BaseModel):
    """Schema for updating a message"""
    is_read: Optional[bool] = None


class MessageInDB(MessageBase):
    """Message schema in database"""
    id: int
    link_id: int
    sender_id: int
    receiver_id: Optional[int] = None
    sales_rep_id: Optional[int] = None  # Which sales rep sent this (if from supplier side)
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Message(MessageInDB):
    """Message schema for API responses"""
    pass

