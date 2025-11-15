"""
Consumer model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Consumer(Base):
    """Consumer model (restaurants/hotels)"""
    __tablename__ = "consumers"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, nullable=False, index=True)
    legal_name = Column(String, nullable=True)
    tax_id = Column(String, nullable=True)
    
    # Contact information
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, default="KZ")
    
    # Business details
    business_type = Column(String, nullable=True)  # restaurant, hotel, etc.
    description = Column(Text, nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="consumer", uselist=False)
    links = relationship("Link", back_populates="consumer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="consumer")

