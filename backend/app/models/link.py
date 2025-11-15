"""
Link model - relationship between supplier and consumer
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class LinkStatus(str, enum.Enum):
    """Link status enumeration"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REMOVED = "removed"
    BLOCKED = "blocked"


class Link(Base):
    """Link model - supplier-consumer relationship"""
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    consumer_id = Column(Integer, ForeignKey("consumers.id"), nullable=False, index=True)
    
    status = Column(Enum(LinkStatus), default=LinkStatus.PENDING, nullable=False, index=True)
    
    # Request details
    requested_by_consumer = Column(Boolean, default=True)  # True if consumer requested, False if supplier invited
    request_message = Column(String, nullable=True)
    
    # Timestamps
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="links")
    consumer = relationship("Consumer", back_populates="links")
    
    # Ensure unique supplier-consumer pairs
    __table_args__ = (
        UniqueConstraint('supplier_id', 'consumer_id', name='unique_supplier_consumer'),
    )

