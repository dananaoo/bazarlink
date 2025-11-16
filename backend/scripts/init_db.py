"""
Database initialization script
Creates all tables and a test user for development
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

from sqlalchemy.exc import OperationalError
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import *  # Import all models to register them
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] Tables created successfully!")
        return True
    except OperationalError as e:
        print(f"[ERROR] Cannot connect to database: {e}")
        print(f"\nCurrent DATABASE_URL: {settings.DATABASE_URL}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. If using Docker: docker-compose up db -d")
        print("3. Check your .env file has correct DATABASE_URL")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        return False


def create_test_user():
    """Create a test user for development"""
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == "admin@test.com").first()
        if existing:
            print(f"[INFO] Test user already exists: {existing.email} (ID: {existing.id})")
            return existing
        
        # Create test user
        user = User(
            email="admin@test.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Test Admin",
            phone="+1234567890",
            role=UserRole.OWNER,
            is_active=True,
            language="en"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"[OK] Test user created: {user.email} (ID: {user.id})")
        return user
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to create user: {e}")
        raise
    finally:
        db.close()


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60)
    
    if not create_tables():
        print("\n[FAILED] Could not create tables. Please fix database connection.")
        sys.exit(1)
    
    print("\nCreating test user...")
    create_test_user()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Database initialized!")
    print("=" * 60)
    print("\nTest user credentials:")
    print("  Email:    admin@test.com")
    print("  Password: admin123")
    print("  Role:     owner")
    print("\nYou can now:")
    print("1. Start FastAPI: uvicorn app.main:app --reload")
    print("2. Open http://localhost:8000/docs")
    print("3. Login at /api/v1/auth/login")
    print("=" * 60)


if __name__ == "__main__":
    main()

