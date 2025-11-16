"""
FastAPI dependencies for authentication and database
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="Bearer",
    description="Enter your email as username and password. Leave client_id and client_secret empty."
)


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    import logging
    logger = logging.getLogger(__name__)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = decode_access_token(token)
        if payload is None:
            logger.warning("Token decode failed: payload is None")
            raise credentials_exception
        
        logger.debug(f"Token payload decoded: {payload}")
        
        # Extract user ID (JWT stores it as string, convert to int)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            logger.warning(f"Token payload missing 'sub' field: {payload}")
            raise credentials_exception
        
        # Convert to int (JWT may store as string)
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            logger.warning(f"Invalid user_id in token: {user_id_str}")
            raise credentials_exception
        
        logger.debug(f"Extracted user_id: {user_id}")
        
        # Query user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logger.warning(f"User not found in database for user_id: {user_id}")
            raise credentials_exception
        
        logger.debug(f"User found: {user.email}, role: {user.role}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}", exc_info=True)
        raise credentials_exception


def require_role(*allowed_roles: UserRole):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

