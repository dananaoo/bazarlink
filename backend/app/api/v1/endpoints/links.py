"""
Link endpoints (supplier-consumer relationships)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.dependencies import get_db, get_current_user
from app.models.user import UserRole
from app.models.link import Link, LinkStatus
from app.models.complaint import Complaint, ComplaintStatus
from app.schemas.link import Link as LinkSchema, LinkCreate, LinkUpdate

router = APIRouter()


def add_complaint_flags_to_links(links: List[Link], db: Session) -> List[dict]:
    """Add has_active_complaint flag to links"""
    result = []
    for link in links:
        # Check if link has active (unresolved) complaints
        active_complaints = db.query(Complaint).filter(
            Complaint.link_id == link.id,
            Complaint.status != ComplaintStatus.RESOLVED
        ).count()
        
        link_dict = {
            "id": link.id,
            "supplier_id": link.supplier_id,
            "consumer_id": link.consumer_id,
            "status": link.status,
            "requested_by_consumer": link.requested_by_consumer,
            "request_message": link.request_message,
            "assigned_sales_rep_id": link.assigned_sales_rep_id,
            "requested_at": link.requested_at,
            "responded_at": link.responded_at,
            "created_at": link.created_at,
            "updated_at": link.updated_at,
            "has_active_complaint": active_complaints > 0
        }
        result.append(link_dict)
    return result


@router.post("/", response_model=LinkSchema, status_code=status.HTTP_201_CREATED)
async def create_link(
    link_in: LinkCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a link request (Consumer or Supplier)"""
    # Check if link already exists
    existing_link = db.query(Link).filter(
        Link.supplier_id == link_in.supplier_id,
        Link.consumer_id == link_in.consumer_id
    ).first()
    
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Link already exists between these supplier and consumer"
        )
    
    requested_by_consumer = current_user.role == UserRole.CONSUMER
    
    db_link = Link(
        **link_in.model_dump(),
        status=LinkStatus.PENDING,
        requested_by_consumer=requested_by_consumer
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    
    return db_link


@router.get("/", response_model=List[LinkSchema])
async def get_links(
    supplier_id: int = None,
    consumer_id: int = None,
    status: LinkStatus = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of links"""
    query = db.query(Link)
    
    if supplier_id:
        query = query.filter(Link.supplier_id == supplier_id)
    if consumer_id:
        query = query.filter(Link.consumer_id == consumer_id)
    if status:
        query = query.filter(Link.status == status)
    
    links = query.offset(skip).limit(limit).all()
    
    # Add has_active_complaint flag
    return add_complaint_flags_to_links(links, db)


@router.get("/{link_id}", response_model=LinkSchema)
async def get_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get link by ID"""
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Add has_active_complaint flag
    return add_complaint_flags_to_links([link], db)[0]


@router.put("/{link_id}", response_model=LinkSchema)
async def update_link(
    link_id: int,
    link_in: LinkUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update link status (Supplier Owner/Manager only for approval)"""
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Only supplier staff (Owner, Manager, Sales Rep) can approve/reject links
    if link_in.status and link_in.status != link.status:
        if current_user.role not in [UserRole.OWNER, UserRole.MANAGER, UserRole.SALES_REPRESENTATIVE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only supplier staff can approve/reject links"
            )
        
        # Verify user belongs to the supplier
        if current_user.supplier_id != link.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only approve/reject links for your own supplier"
            )
        
        link.status = link_in.status
        link.responded_at = datetime.utcnow()
    else:
        update_data = link_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(link, field, value)
    
    db.commit()
    db.refresh(link)
    
    return link


@router.post("/{link_id}/assign", response_model=LinkSchema)
async def assign_chat(
    link_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assign chat to current sales representative (Sales Rep only)"""
    if current_user.role != UserRole.SALES_REPRESENTATIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sales representatives can assign chats"
        )
    
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Verify link belongs to sales rep's supplier
    if link.supplier_id != current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only assign chats from your own supplier"
        )
    
    # Verify link is accepted
    if link.status != LinkStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only assign accepted links"
        )
    
    # Assign chat to current sales rep
    link.assigned_sales_rep_id = current_user.id
    db.commit()
    db.refresh(link)
    
    return link


@router.post("/{link_id}/unassign", response_model=LinkSchema)
async def unassign_chat(
    link_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Unassign chat (Sales Rep who assigned it, or Manager/Owner)"""
    if current_user.role not in [UserRole.SALES_REPRESENTATIVE, UserRole.MANAGER, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Verify link belongs to user's supplier
    if link.supplier_id != current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only unassign chats from your own supplier"
        )
    
    # Sales rep can only unassign if they assigned it, or if Manager/Owner
    if current_user.role == UserRole.SALES_REPRESENTATIVE:
        if link.assigned_sales_rep_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only unassign chats assigned to you"
            )
    
    # Unassign chat
    link.assigned_sales_rep_id = None
    db.commit()
    db.refresh(link)
    
    return link


@router.get("/chats/my", response_model=List[LinkSchema])
async def get_my_chats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get chats assigned to current sales representative"""
    if current_user.role != UserRole.SALES_REPRESENTATIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sales representatives can view their assigned chats"
        )
    
    if not current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sales representative must be associated with a supplier"
        )
    
    # Get links assigned to this sales rep
    links = db.query(Link).filter(
        Link.supplier_id == current_user.supplier_id,
        Link.assigned_sales_rep_id == current_user.id,
        Link.status == LinkStatus.ACCEPTED
    ).offset(skip).limit(limit).all()
    
    # Add has_active_complaint flag
    return add_complaint_flags_to_links(links, db)


@router.get("/chats/other", response_model=List[LinkSchema])
async def get_other_chats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get chats from same supplier that are not assigned to current sales rep"""
    if current_user.role != UserRole.SALES_REPRESENTATIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sales representatives can view other chats"
        )
    
    if not current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sales representative must be associated with a supplier"
        )
    
    # Get links from same supplier that are either unassigned or assigned to someone else
    links = db.query(Link).filter(
        Link.supplier_id == current_user.supplier_id,
        Link.status == LinkStatus.ACCEPTED
    ).filter(
        (Link.assigned_sales_rep_id != current_user.id) | (Link.assigned_sales_rep_id.is_(None))
    ).offset(skip).limit(limit).all()
    
    # Add has_active_complaint flag
    return add_complaint_flags_to_links(links, db)


@router.get("/chats/consumer", response_model=List[LinkSchema])
async def get_consumer_chats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all accepted chats for current consumer"""
    if current_user.role != UserRole.CONSUMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers can view their chats"
        )
    
    if not current_user.consumer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consumer profile not found"
        )
    
    # Get all accepted links for this consumer
    links = db.query(Link).filter(
        Link.consumer_id == current_user.consumer_id,
        Link.status == LinkStatus.ACCEPTED
    ).offset(skip).limit(limit).all()
    
    # Add has_active_complaint flag
    return add_complaint_flags_to_links(links, db)

