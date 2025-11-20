"""
Consumer endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.consumer import Consumer
from app.models.user import UserRole
from app.schemas.consumer import Consumer as ConsumerSchema, ConsumerCreate, ConsumerUpdate

router = APIRouter()


@router.post("/", response_model=ConsumerSchema, status_code=status.HTTP_201_CREATED)
async def create_consumer(
    consumer_in: ConsumerCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new consumer (Consumer role only)
    
    Note: Normally, consumers are created automatically during registration
    via /api/v1/auth/register-consumer. This endpoint is for edge cases only.
    """
    # Only consumers can create consumer records
    if current_user.role != UserRole.CONSUMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers can create consumer records. Use /api/v1/auth/register-consumer for registration."
        )
    
    # Check if consumer already exists with this email
    existing_consumer = db.query(Consumer).filter(Consumer.email == consumer_in.email).first()
    if existing_consumer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consumer with this email already exists"
        )
    
    # If current user already has a consumer_id, they shouldn't create another one
    if current_user.consumer_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a consumer account. Use update endpoint to modify it."
        )
    
    db_consumer = Consumer(**consumer_in.model_dump())
    db.add(db_consumer)
    db.commit()
    db.refresh(db_consumer)
    
    # Link the created consumer to the current user
    current_user.consumer_id = db_consumer.id
    db.commit()
    
    return db_consumer


@router.get("/", response_model=List[ConsumerSchema])
async def get_consumers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of consumers"""
    consumers = db.query(Consumer).offset(skip).limit(limit).all()
    return consumers


@router.get("/{consumer_id}", response_model=ConsumerSchema)
async def get_consumer(
    consumer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get consumer by ID"""
    consumer = db.query(Consumer).filter(Consumer.id == consumer_id).first()
    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer not found"
        )
    return consumer


@router.put("/{consumer_id}", response_model=ConsumerSchema)
async def update_consumer(
    consumer_id: int,
    consumer_in: ConsumerUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update consumer (Consumer can only update their own record)"""
    consumer = db.query(Consumer).filter(Consumer.id == consumer_id).first()
    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer not found"
        )
    
    # Only consumers can update consumer records
    if current_user.role != UserRole.CONSUMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers can update consumer records"
        )
    
    # Consumers can only update their own consumer record
    if current_user.consumer_id != consumer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own consumer record"
        )
    
    update_data = consumer_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(consumer, field, value)
    
    db.commit()
    db.refresh(consumer)
    
    return consumer

