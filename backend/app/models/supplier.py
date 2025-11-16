"""
Supplier model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class VerificationStatus(str, enum.Enum):
    """Supplier verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Supplier(Base):
    """Supplier model"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)
    legal_name = Column(String, nullable=True)
    tax_id = Column(String, nullable=True, unique=True)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    
    # Contact information
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, default="KZ")  # Kazakhstan
    
    # Business details
    description = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    staff = relationship("User", back_populates="supplier")
    products = relationship("Product", back_populates="supplier", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="supplier", cascade="all, delete-orphan")
    links = relationship("Link", back_populates="supplier", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="supplier")

