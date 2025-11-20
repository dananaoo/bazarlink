"""
Complaint schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.complaint import ComplaintStatus, ComplaintLevel


class ComplaintBase(BaseModel):
    """Base complaint schema"""
    title: str
    description: str
    order_id: int


class ComplaintCreate(ComplaintBase):
    """Schema for creating a complaint"""
    pass


class ComplaintUpdate(BaseModel):
    """Schema for updating a complaint"""
    status: Optional[ComplaintStatus] = None
    resolution: Optional[str] = None
    level: Optional[ComplaintLevel] = None


class ComplaintEscalate(BaseModel):
    """Schema for escalating a complaint"""
    escalated_to_user_id: int
    note: Optional[str] = None


class ComplaintInDB(ComplaintBase):
    """Complaint schema in database"""
    id: int
    consumer_id: int
    supplier_id: int
    link_id: int  # Link to chat for this complaint
    status: ComplaintStatus
    level: ComplaintLevel
    escalated_to_user_id: Optional[int] = None
    escalated_by_user_id: Optional[int] = None
    resolution: Optional[str] = None
    resolved_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Complaint(ComplaintInDB):
    """Complaint schema for API responses"""
    pass

