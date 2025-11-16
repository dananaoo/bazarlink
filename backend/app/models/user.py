"""
User model - represents all user types (Consumer, Owner, Manager, Sales Representative)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    CONSUMER = "consumer"
    OWNER = "owner"
    MANAGER = "manager"
    SALES_REPRESENTATIVE = "sales_representative"
    
    def __str__(self):
        return self.value


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    language = Column(String, default="en")  # kk, ru, en
    
    # Foreign keys
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)  # For supplier staff
    consumer_id = Column(Integer, ForeignKey("consumers.id"), nullable=True)  # For consumers
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="staff")
    consumer = relationship("Consumer", back_populates="user")

