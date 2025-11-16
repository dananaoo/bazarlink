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
from app.schemas.link import Link as LinkSchema, LinkCreate, LinkUpdate

router = APIRouter()


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
    return links


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
    return link


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

