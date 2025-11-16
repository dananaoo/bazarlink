"""
User endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate, OwnershipTransferRequest
from app.core.security import get_password_hash

router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.OWNER))
):
    """Create a new user (Owner only) - can only create Managers and Sales Reps"""
    # Owner can only create Managers and Sales Representatives
    if user_in.role not in [UserRole.MANAGER, UserRole.SALES_REPRESENTATIVE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owners can only create Managers and Sales Representatives"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Verify owner has a supplier
    if not current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner must be associated with a supplier"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=user_in.role,
        language=user_in.language,
        supplier_id=current_user.supplier_id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_self(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete own account (Consumer and Owner only)
    
    For Owners: Prevents deletion if there are other staff members (Managers/Sales Reps).
    You must transfer ownership first or delete other staff members.
    
    For Consumers: Deletes both User and Consumer records (cascade).
    """
    # Only consumers and owners can delete themselves
    if current_user.role not in [UserRole.CONSUMER, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers and owners can delete their own accounts"
        )
    
    # For Owners: Check if there are other staff members
    if current_user.role == UserRole.OWNER:
        if not current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner must be associated with a supplier"
            )
        
        # Check if there are other staff members (Managers or Sales Reps)
        other_staff = db.query(User).filter(
            User.supplier_id == current_user.supplier_id,
            User.id != current_user.id,
            User.role.in_([UserRole.MANAGER, UserRole.SALES_REPRESENTATIVE])
        ).count()
        
        if other_staff > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete owner account. There are {other_staff} staff member(s) still associated with this supplier. "
                       "Please transfer ownership to a Manager first or delete other staff members."
            )
        
        # If no other staff, we can delete the owner
        # Note: Supplier will remain but without an owner (could be handled by admin later)
        # Or we could delete the supplier too - but that's very destructive
    
    # For Consumers: Delete the Consumer record as well (cascade)
    if current_user.role == UserRole.CONSUMER and current_user.consumer_id:
        from app.models.consumer import Consumer
        consumer = db.query(Consumer).filter(Consumer.id == current_user.consumer_id).first()
        if consumer:
            db.delete(consumer)
    
    # Delete the user
    db.delete(current_user)
    db.commit()
    
    return None


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a user (Owner can delete Managers/Sales Reps, Manager can delete Sales Reps)"""
    # Find the user to delete
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-deletion via this endpoint (use /me instead)
    if user_to_delete.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself. Use DELETE /users/me endpoint instead"
        )
    
    # Owner can delete Managers and Sales Representatives from their supplier
    if current_user.role == UserRole.OWNER:
        # Verify owner has a supplier
        if not current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner must be associated with a supplier"
            )
        
        # Owner can only delete Managers and Sales Reps
        if user_to_delete.role not in [UserRole.MANAGER, UserRole.SALES_REPRESENTATIVE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Owners can only delete Managers and Sales Representatives"
            )
        
        # Verify the user belongs to the same supplier
        if user_to_delete.supplier_id != current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only delete users from your own supplier"
            )
    
    # Manager can delete Sales Representatives from their supplier
    elif current_user.role == UserRole.MANAGER:
        # Verify manager has a supplier
        if not current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manager must be associated with a supplier"
            )
        
        # Manager can only delete Sales Reps
        if user_to_delete.role != UserRole.SALES_REPRESENTATIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers can only delete Sales Representatives"
            )
        
        # Verify the user belongs to the same supplier
        if user_to_delete.supplier_id != current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only delete users from your own supplier"
            )
    
    else:
        # Other roles cannot delete users
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete users"
        )
    
    # For Sales Reps: If deleting a Sales Rep, also check if we need to clean up any related data
    # (Currently no cascade needed as relationships are handled by foreign keys)
    
    # Delete the user
    db.delete(user_to_delete)
    db.commit()
    
    return None


@router.post("/transfer-ownership", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def transfer_ownership(
    transfer_data: OwnershipTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.OWNER))
):
    """Transfer ownership from current owner to a Manager (Owner only)
    
    This allows the current owner to transfer their ownership to a Manager.
    After transfer:
    - The Manager becomes the new Owner
    - The current owner becomes a Manager (or can be deleted)
    """
    # Verify current owner has a supplier
    if not current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner must be associated with a supplier"
        )
    
    # Find the new owner (must be a Manager)
    new_owner = db.query(User).filter(User.id == transfer_data.new_owner_user_id).first()
    if not new_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify the new owner is a Manager
    if new_owner.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only transfer ownership to a Manager"
        )
    
    # Verify the new owner belongs to the same supplier
    if new_owner.supplier_id != current_user.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only transfer ownership to a Manager from your own supplier"
        )
    
    # Prevent self-transfer
    if new_owner.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer ownership to yourself"
        )
    
    # Transfer ownership: Make Manager the new Owner
    new_owner.role = UserRole.OWNER
    
    # Optionally: Convert current owner to Manager (or they can delete themselves)
    # For now, we'll keep the current owner as Owner too (so there can be multiple owners)
    # If you want to demote the current owner, uncomment the next line:
    # current_user.role = UserRole.MANAGER
    
    db.commit()
    db.refresh(new_owner)
    
    return new_owner

