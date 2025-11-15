"""
Consumer endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.consumer import Consumer
from app.schemas.consumer import Consumer as ConsumerSchema, ConsumerCreate, ConsumerUpdate

router = APIRouter()


@router.post("/", response_model=ConsumerSchema, status_code=status.HTTP_201_CREATED)
async def create_consumer(
    consumer_in: ConsumerCreate,
    db: Session = Depends(get_db)
):
    """Create a new consumer"""
    existing_consumer = db.query(Consumer).filter(Consumer.email == consumer_in.email).first()
    if existing_consumer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consumer with this email already exists"
        )
    
    db_consumer = Consumer(**consumer_in.model_dump())
    db.add(db_consumer)
    db.commit()
    db.refresh(db_consumer)
    
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
    """Update consumer"""
    consumer = db.query(Consumer).filter(Consumer.id == consumer_id).first()
    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer not found"
        )
    
    update_data = consumer_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(consumer, field, value)
    
    db.commit()
    db.refresh(consumer)
    
    return consumer

