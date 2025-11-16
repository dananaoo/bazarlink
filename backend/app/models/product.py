"""
Product model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class ProductUnit(str, enum.Enum):
    """Product unit types"""
    KILOGRAM = "kg"
    GRAM = "g"
    LITER = "l"
    MILLILITER = "ml"
    PIECE = "piece"
    BOX = "box"
    PACK = "pack"


class Product(Base):
    """Product model"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    
    # Product information
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String, nullable=True, index=True)  # Stock Keeping Unit
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    discount_price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String, default="KZT")  # Kazakhstani Tenge
    
    # Inventory
    stock_quantity = Column(Numeric(10, 2), default=0)
    unit = Column(Enum(ProductUnit), nullable=False, default=ProductUnit.KILOGRAM)
    min_order_quantity = Column(Numeric(10, 2), default=1)
    
    # Availability
    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Delivery options
    delivery_available = Column(Boolean, default=True)
    pickup_available = Column(Boolean, default=True)
    lead_time_days = Column(Integer, default=1)  # Days until delivery
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

