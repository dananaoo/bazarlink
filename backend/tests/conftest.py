"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.core.dependencies import get_db
from app.models.user import User, UserRole
from app.models.supplier import Supplier, VerificationStatus
from app.models.consumer import Consumer
from app.core.security import get_password_hash


# Test database URL (in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)  # Recreate for next test


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        # Use the same db_session for all requests in this test
        yield db_session
    
    # Override get_db dependency to use test database session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def test_supplier(db_session):
    """Create a test supplier"""
    supplier = Supplier(
        company_name="Test Supplier",
        legal_name="Test Supplier LLC",
        email="supplier@test.com",
        phone="+1234567890",
        city="Almaty",
        country="KZ",
        verification_status=VerificationStatus.VERIFIED,
        is_active=True
    )
    db_session.add(supplier)
    db_session.commit()
    db_session.refresh(supplier)
    return supplier


@pytest.fixture
def test_consumer(db_session):
    """Create a test consumer"""
    consumer = Consumer(
        business_name="Test Restaurant",
        legal_name="Test Restaurant LLC",
        email="consumer@test.com",
        phone="+1234567891",
        city="Almaty",
        country="KZ",
        business_type="restaurant",
        is_active=True
    )
    db_session.add(consumer)
    db_session.commit()
    db_session.refresh(consumer)
    return consumer


@pytest.fixture
def test_owner_user(db_session, test_supplier):
    """Create a test owner user"""
    user = User(
        email="owner@test.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test Owner",
        role=UserRole.OWNER,
        supplier_id=test_supplier.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_consumer_user(db_session, test_consumer):
    """Create a test consumer user"""
    user = User(
        email="consumer@test.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test Consumer",
        role=UserRole.CONSUMER,
        consumer_id=test_consumer.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers_owner(client, test_owner_user):
    """Get auth headers for owner user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_owner_user.email,
            "password": "testpassword"
        }
    )
    assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
    data = response.json()
    assert "access_token" in data, f"No access_token in response: {data}"
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_consumer(client, test_consumer_user):
    """Get auth headers for consumer user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_consumer_user.email,
            "password": "testpassword"
        }
    )
    assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
    data = response.json()
    assert "access_token" in data, f"No access_token in response: {data}"
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}

