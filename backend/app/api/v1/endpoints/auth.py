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
    import logging
    logger = logging.getLogger(__name__)
    print(f"\n[LOGIN] Login attempt for email: {form_data.username}")
    logger.info(f"Login attempt for email: {form_data.username}")
    
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
        
        print(f"[LOGIN] Login successful for user: {user.email} (ID: {user.id})")
        logger.info(f"Login successful for user: {user.email} (ID: {user.id})")
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
    from app.models.supplier import Supplier
    from app.models.user import UserRole
    from app.core.security import get_password_hash
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Owner registration attempt started")
        
        # Parse registration data
        user_data = registration_data
        supplier_data = user_data.get("supplier", {})
        
        logger.debug(f"Registration data received: email={user_data.get('email')}, supplier_name={supplier_data.get('company_name')}")
        
        # Validate required fields
        if not user_data.get("email") or not user_data.get("password") or not user_data.get("full_name"):
            logger.warning("Registration failed: Missing required fields")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: email, password, full_name"
            )
        
        if not supplier_data or not supplier_data.get("company_name"):
            logger.warning("Registration failed: Missing supplier information")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing supplier information (company_name is required)"
            )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            logger.warning(f"Registration failed: User already exists - {user_data['email']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create supplier first
        supplier_email = supplier_data.get("email") or user_data["email"]
        existing_supplier = db.query(Supplier).filter(Supplier.email == supplier_email).first()
        if existing_supplier:
            logger.warning(f"Registration failed: Supplier already exists - {supplier_email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier with this email already exists"
            )
        
        # Ensure supplier has email
        if not supplier_data.get("email"):
            supplier_data["email"] = user_data["email"]
        
        logger.info(f"Creating supplier: {supplier_data.get('company_name')}")
        db_supplier = Supplier(**supplier_data)
        db.add(db_supplier)
        db.flush()  # Get supplier ID
        
        logger.info(f"Creating owner user: {user_data['email']}, supplier_id={db_supplier.id}")
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
        
        logger.info(f"Owner registration successful: user_id={db_user.id}, email={db_user.email}")
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during owner registration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

