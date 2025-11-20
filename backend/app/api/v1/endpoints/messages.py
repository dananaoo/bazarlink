"""
Message endpoints for chat functionality
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.dependencies import get_db, get_current_user
from app.models.user import UserRole
from app.models.message import Message
from app.models.link import Link, LinkStatus
from app.schemas.message import Message as MessageSchema, MessageCreate, MessageUpdate

router = APIRouter()


@router.post("/", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_in: MessageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new message (Consumer, Sales Rep, Manager, or Owner)"""
    # Verify link exists and is accepted
    link = db.query(Link).filter(Link.id == message_in.link_id).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Only consumers and supplier staff can send messages
    if current_user.role == UserRole.CONSUMER:
        if link.consumer_id != current_user.consumer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only send messages in your own links"
            )
        if link.status != LinkStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Link must be accepted before sending messages"
            )
        # Consumer messages go to supplier (receiver_id can be None for general supplier chat)
        receiver_id = message_in.receiver_id  # Optional: specific sales rep, or None for general
    elif current_user.role in [UserRole.SALES_REPRESENTATIVE, UserRole.MANAGER, UserRole.OWNER]:
        if link.supplier_id != current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only send messages in links for your supplier"
            )
        if link.status != LinkStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Link must be accepted before sending messages"
            )
        # Supplier staff messages go to consumer - find consumer's user
        from app.models.consumer import Consumer
        consumer = db.query(Consumer).filter(Consumer.id == link.consumer_id).first()
        receiver_id = consumer.user.id if consumer and consumer.user else None
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers and supplier staff can send messages"
        )
    
    # Validate that either content or attachment_url is provided
    if not message_in.content and not message_in.attachment_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either content or attachment_url must be provided"
        )
    
    # If attachment is provided, set message_type to "attachment"
    if message_in.attachment_url:
        message_type = "attachment"
    else:
        message_type = message_in.message_type or "text"
    
    # Determine sales_rep_id (only for sales rep messages, not for managers/owners)
    sales_rep_id = None
    if current_user.role == UserRole.SALES_REPRESENTATIVE:
        sales_rep_id = current_user.id
    
    db_message = Message(
        link_id=message_in.link_id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        sales_rep_id=sales_rep_id,
        content=message_in.content or "",  # Empty string if None
        message_type=message_type,
        attachment_url=message_in.attachment_url,
        attachment_type=message_in.attachment_type,
        product_id=message_in.product_id,
        order_id=message_in.order_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message


@router.get("/", response_model=List[MessageSchema])
async def get_messages(
    link_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get messages for a link (Consumer or Sales Rep)"""
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.CONSUMER:
        if link.consumer_id != current_user.consumer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif current_user.role in [UserRole.SALES_REPRESENTATIVE, UserRole.MANAGER, UserRole.OWNER]:
        if link.supplier_id != current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get messages
    messages = db.query(Message).filter(
        Message.link_id == link_id
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
    # Mark messages as read if current user is receiver
    for message in messages:
        if message.receiver_id == current_user.id and not message.is_read:
            message.is_read = True
            message.read_at = datetime.utcnow()
    
    db.commit()
    
    return list(reversed(messages))  # Return in chronological order


@router.put("/{message_id}/read", response_model=MessageSchema)
async def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark a message as read"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if message.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only mark your own received messages as read"
        )
    
    message.is_read = True
    message.read_at = datetime.utcnow()
    db.commit()
    db.refresh(message)
    
    return message

