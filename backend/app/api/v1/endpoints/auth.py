"""
Authentication endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.core.dependencies import get_db
from app.models.user import User
from app.schemas.user import Token, User as UserSchema
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """User login endpoint"""
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Handle role - it might be a string or enum
        role_value = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": role_value},  # Convert user.id to string for JWT
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/register-owner", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_owner(
    registration_data: dict,
    db: Session = Depends(get_db)
):
    """Register a new owner with supplier (Public endpoint)"""
    from app.schemas.auth import OwnerRegistration
    from app.models.supplier import Supplier
    from app.models.user import UserRole
    from app.core.security import get_password_hash
    
    # Parse registration data
    if isinstance(registration_data, dict):
        # Handle dict input
        user_data = registration_data
        supplier_data = user_data.get("supplier", {})
    else:
        # Handle Pydantic model
        user_data = registration_data.model_dump()
        supplier_data = user_data.get("supplier", {})
    
    # Validate required fields
    if not user_data.get("email") or not user_data.get("password") or not user_data.get("full_name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields: email, password, full_name"
        )
    
    if not supplier_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing supplier information"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data["email"]).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create supplier first
    existing_supplier = db.query(Supplier).filter(Supplier.email == supplier_data.get("email")).first()
    if existing_supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier with this email already exists"
        )
    
    db_supplier = Supplier(**supplier_data)
    db.add(db_supplier)
    db.flush()  # Get supplier ID
    
    # Create owner user
    hashed_password = get_password_hash(user_data["password"])
    db_user = User(
        email=user_data["email"],
        hashed_password=hashed_password,
        full_name=user_data["full_name"],
        phone=user_data.get("phone"),
        role=UserRole.OWNER,
        language=user_data.get("language", "en"),
        supplier_id=db_supplier.id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

