"""
Incident endpoints for managers and owners to handle escalated problems
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import UserRole
from app.models.incident import Incident, IncidentStatus
from app.models.complaint import Complaint, ComplaintLevel
from app.schemas.incident import Incident as IncidentSchema, IncidentCreate, IncidentUpdate

router = APIRouter()


@router.post("/", response_model=IncidentSchema, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: IncidentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.MANAGER, UserRole.OWNER))
):
    """Create an incident (Manager and Owner only)"""
    # Get supplier_id from current user
    if not current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a supplier"
        )
    
    # If order_id provided, get consumer_id and supplier_id from order
    consumer_id = None
    supplier_id = current_user.supplier_id
    
    if incident_in.order_id:
        from app.models.order import Order
        order = db.query(Order).filter(Order.id == incident_in.order_id).first()
        if order:
            consumer_id = order.consumer_id
            supplier_id = order.supplier_id
    
    db_incident = Incident(
        order_id=incident_in.order_id,
        consumer_id=consumer_id,
        supplier_id=supplier_id,
        title=incident_in.title,
        description=incident_in.description,
        status=IncidentStatus.OPEN,
        assigned_to_user_id=incident_in.assigned_to_user_id or current_user.id,
        created_by_user_id=current_user.id
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    
    return db_incident


@router.get("/", response_model=List[IncidentSchema])
async def get_incidents(
    supplier_id: int = None,
    status: IncidentStatus = None,
    assigned_to_user_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.MANAGER, UserRole.OWNER))
):
    """Get incidents (Manager and Owner only - escalated problems)"""
    query = db.query(Incident)
    
    # Managers and Owners only see incidents for their supplier
    if current_user.supplier_id:
        query = query.filter(Incident.supplier_id == current_user.supplier_id)
    
    if supplier_id:
        query = query.filter(Incident.supplier_id == supplier_id)
    if status:
        query = query.filter(Incident.status == status)
    if assigned_to_user_id:
        query = query.filter(Incident.assigned_to_user_id == assigned_to_user_id)
    
    incidents = query.offset(skip).limit(limit).all()
    return incidents


@router.get("/{incident_id}", response_model=IncidentSchema)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.MANAGER, UserRole.OWNER))
):
    """Get incident by ID (Manager and Owner only)"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Check permissions
    if incident.supplier_id != current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return incident


@router.put("/{incident_id}", response_model=IncidentSchema)
async def update_incident(
    incident_id: int,
    incident_in: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.MANAGER, UserRole.OWNER))
):
    """Update incident (Manager and Owner only)"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Check permissions
    if incident.supplier_id != current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update fields
    if incident_in.status:
        incident.status = incident_in.status
        if incident_in.status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.utcnow()
            incident.resolved_by_user_id = current_user.id
    
    if incident_in.resolution:
        incident.resolution = incident_in.resolution
    
    if incident_in.assigned_to_user_id:
        # Verify assigned user is a manager or sales rep in same supplier
        from app.models.user import User
        assigned_user = db.query(User).filter(User.id == incident_in.assigned_to_user_id).first()
        if assigned_user and assigned_user.supplier_id == current_user.supplier_id:
            incident.assigned_to_user_id = incident_in.assigned_to_user_id
    
    db.commit()
    db.refresh(incident)
    
    return incident

