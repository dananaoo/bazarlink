"""
Complaint endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.dependencies import get_db, get_current_user
from app.models.user import UserRole
from app.models.complaint import Complaint, ComplaintStatus, ComplaintLevel
from app.models.order import Order
from app.models.link import Link, LinkStatus
from app.schemas.complaint import Complaint as ComplaintSchema, ComplaintCreate, ComplaintUpdate, ComplaintEscalate

router = APIRouter()


@router.post("/", response_model=ComplaintSchema, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    complaint_in: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a complaint (Consumer only)
    
    Automatically creates first message in the chat with complaint details.
    Requires an ACCEPTED link (not BLOCKED) between consumer and supplier.
    """
    if current_user.role != UserRole.CONSUMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers can create complaints"
        )
    
    # Verify order exists and belongs to consumer
    order = db.query(Order).filter(Order.id == complaint_in.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.consumer_id != current_user.consumer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create complaints for your own orders"
        )
    
    # Check if ACCEPTED link exists between consumer and supplier
    link = db.query(Link).filter(
        Link.consumer_id == order.consumer_id,
        Link.supplier_id == order.supplier_id,
        Link.status == LinkStatus.ACCEPTED
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must have an accepted link with the supplier to create a complaint"
        )
    
    # Check that link is not BLOCKED
    if link.status == LinkStatus.BLOCKED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create complaint: your link with this supplier is blocked"
        )
    
    # Create complaint
    db_complaint = Complaint(
        order_id=complaint_in.order_id,
        consumer_id=order.consumer_id,
        supplier_id=order.supplier_id,
        link_id=link.id,
        title=complaint_in.title,
        description=complaint_in.description,
        status=ComplaintStatus.OPEN,
        level=ComplaintLevel.SALES
    )
    db.add(db_complaint)
    db.flush()  # Flush to get complaint.id
    
    # Create first message in chat with complaint details
    from app.models.message import Message
    complaint_message = f"Жалоба: {complaint_in.title}\n\n{complaint_in.description}"
    
    # Find consumer's user to set as sender
    from app.models.consumer import Consumer
    consumer = db.query(Consumer).filter(Consumer.id == order.consumer_id).first()
    sender_id = consumer.user.id if consumer and consumer.user else current_user.id
    
    db_message = Message(
        link_id=link.id,
        sender_id=sender_id,
        receiver_id=None,  # Message to supplier (general)
        content=complaint_message,
        message_type="text",
        order_id=order.id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_complaint)
    
    return db_complaint


@router.get("/", response_model=List[ComplaintSchema])
async def get_complaints(
    supplier_id: int = None,
    consumer_id: int = None,
    status: ComplaintStatus = None,
    level: ComplaintLevel = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get complaints"""
    query = db.query(Complaint)
    
    # Role-based filtering
    if current_user.role == UserRole.CONSUMER:
        query = query.filter(Complaint.consumer_id == current_user.consumer_id)
    elif current_user.role == UserRole.SALES_REPRESENTATIVE:
        # Sales reps see complaints at SALES level for their supplier
        query = query.filter(
            Complaint.supplier_id == current_user.supplier_id,
            Complaint.level == ComplaintLevel.SALES
        )
    elif current_user.role == UserRole.MANAGER:
        # Managers see escalated complaints (MANAGER level) for their supplier
        query = query.filter(
            Complaint.supplier_id == current_user.supplier_id,
            Complaint.level == ComplaintLevel.MANAGER
        )
    elif current_user.role == UserRole.OWNER:
        # Owners see all complaints for their supplier (including escalated)
        query = query.filter(
            Complaint.supplier_id == current_user.supplier_id
        )
    
    if supplier_id:
        query = query.filter(Complaint.supplier_id == supplier_id)
    if consumer_id:
        query = query.filter(Complaint.consumer_id == consumer_id)
    if status:
        query = query.filter(Complaint.status == status)
    if level:
        query = query.filter(Complaint.level == level)
    
    complaints = query.offset(skip).limit(limit).all()
    return complaints


@router.get("/{complaint_id}", response_model=ComplaintSchema)
async def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get complaint by ID"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.CONSUMER:
        if complaint.consumer_id != current_user.consumer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif current_user.role == UserRole.SALES_REPRESENTATIVE:
        if complaint.supplier_id != current_user.supplier_id or complaint.level != ComplaintLevel.SALES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif current_user.role == UserRole.MANAGER:
        if complaint.supplier_id != current_user.supplier_id or complaint.level != ComplaintLevel.MANAGER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif current_user.role == UserRole.OWNER:
        # Owners can view all complaints for their supplier (including escalated)
        if complaint.supplier_id != current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return complaint


@router.post("/{complaint_id}/escalate", response_model=ComplaintSchema)
async def escalate_complaint(
    complaint_id: int,
    escalate_in: ComplaintEscalate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Escalate complaint to manager (Sales Rep only)"""
    if current_user.role != UserRole.SALES_REPRESENTATIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sales representatives can escalate complaints"
        )
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    if complaint.supplier_id != current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if complaint.level != ComplaintLevel.SALES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complaint is already escalated"
        )
    
    # Verify target user is a manager
    from app.models.user import User
    target_user = db.query(User).filter(User.id == escalate_in.escalated_to_user_id).first()
    if not target_user or target_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target user must be a manager"
        )
    
    complaint.level = ComplaintLevel.MANAGER
    complaint.escalated_to_user_id = escalate_in.escalated_to_user_id
    complaint.escalated_by_user_id = current_user.id
    complaint.status = ComplaintStatus.ESCALATED
    
    db.commit()
    db.refresh(complaint)
    
    return complaint


@router.put("/{complaint_id}", response_model=ComplaintSchema)
async def update_complaint(
    complaint_id: int,
    complaint_in: ComplaintUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update complaint (Sales Rep, Manager, or Owner)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.SALES_REPRESENTATIVE:
        if complaint.supplier_id != current_user.supplier_id or complaint.level != ComplaintLevel.SALES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif current_user.role == UserRole.MANAGER:
        if complaint.supplier_id != current_user.supplier_id or complaint.level != ComplaintLevel.MANAGER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif current_user.role == UserRole.OWNER:
        # Owners can update all complaints for their supplier (including escalated)
        if complaint.supplier_id != current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sales representatives, managers, and owners can update complaints"
        )
    
    # Update fields
    if complaint_in.status:
        complaint.status = complaint_in.status
        if complaint_in.status == ComplaintStatus.RESOLVED:
            complaint.resolved_at = datetime.utcnow()
            complaint.resolved_by_user_id = current_user.id
    
    if complaint_in.resolution:
        complaint.resolution = complaint_in.resolution
    
    if complaint_in.level:
        complaint.level = complaint_in.level
    
    db.commit()
    db.refresh(complaint)
    
    return complaint

