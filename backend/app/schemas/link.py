"""
Link schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.link import LinkStatus


class LinkBase(BaseModel):
    """Base link schema"""
    supplier_id: int
    consumer_id: int
    request_message: Optional[str] = None


class LinkCreate(LinkBase):
    """Schema for creating a link request"""
    pass


class LinkUpdate(BaseModel):
    """Schema for updating a link"""
    status: Optional[LinkStatus] = None


class LinkInDB(LinkBase):
    """Link schema in database"""
    id: int
    status: LinkStatus
    requested_by_consumer: bool
    requested_at: datetime
    responded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Link(LinkInDB):
    """Link schema for API responses"""
    pass

