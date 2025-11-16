"""
Incident schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.incident import IncidentStatus


class IncidentBase(BaseModel):
    """Base incident schema"""
    title: str
    description: str
    order_id: Optional[int] = None


class IncidentCreate(IncidentBase):
    """Schema for creating an incident"""
    assigned_to_user_id: Optional[int] = None


class IncidentUpdate(BaseModel):
    """Schema for updating an incident"""
    status: Optional[IncidentStatus] = None
    resolution: Optional[str] = None
    assigned_to_user_id: Optional[int] = None


class IncidentInDB(IncidentBase):
    """Incident schema in database"""
    id: int
    consumer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    status: IncidentStatus
    assigned_to_user_id: Optional[int] = None
    created_by_user_id: int
    resolution: Optional[str] = None
    resolved_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Incident(IncidentInDB):
    """Incident schema for API responses"""
    pass

