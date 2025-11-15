"""
Complaint model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class ComplaintStatus(str, enum.Enum):
    """Complaint status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class ComplaintLevel(str, enum.Enum):
    """Complaint escalation level"""
    SALES = "sales"
    MANAGER = "manager"
    OWNER = "owner"


class Complaint(Base):
    """Complaint model"""
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    consumer_id = Column(Integer, ForeignKey("consumers.id"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    
    # Complaint details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.OPEN, nullable=False, index=True)
    level = Column(Enum(ComplaintLevel), default=ComplaintLevel.SALES, nullable=False)
    
    # Escalation
    escalated_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    escalated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Resolution
    resolution = Column(Text, nullable=True)
    resolved_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="complaints")
    escalated_to = relationship("User", foreign_keys=[escalated_to_user_id])
    escalated_by = relationship("User", foreign_keys=[escalated_by_user_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_user_id])

