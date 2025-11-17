"""
Message model for chat functionality
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Message(Base):
    """Message model for chat"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("links.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    sales_rep_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Which sales rep sent this (if from supplier side)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, receipt, product_link, attachment
    
    # Attachments
    attachment_url = Column(String, nullable=True)
    attachment_type = Column(String, nullable=True)  # image, document, audio, etc.
    
    # Product link (if message references a product)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    # Order receipt (if message references an order)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    # Canned reply reference
    is_canned_reply = Column(Boolean, default=False)
    canned_reply_id = Column(Integer, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    link = relationship("Link")
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    sales_rep = relationship("User", foreign_keys=[sales_rep_id])
    product = relationship("Product")
    order = relationship("Order")

