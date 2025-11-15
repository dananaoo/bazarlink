"""
Tests for user endpoints
"""
import pytest
from fastapi import status
from app.models.user import UserRole


def test_create_user_as_owner(client, auth_headers_owner, test_supplier):
    """Test creating a user as owner"""
    user_data = {
        "email": "newuser@test.com",
        "password": "newpassword",
        "full_name": "New User",
        "phone": "+1234567892",
        "role": UserRole.MANAGER.value,
        "language": "en"
    }
    response = client.post(
        "/api/v1/users/",
        json=user_data,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]


def test_create_user_duplicate_email(client, auth_headers_owner, test_owner_user):
    """Test creating user with duplicate email"""
    user_data = {
        "email": test_owner_user.email,
        "password": "password",
        "full_name": "Duplicate User",
        "role": UserRole.MANAGER.value
    }
    response = client.post(
        "/api/v1/users/",
        json=user_data,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_user_unauthorized(client):
    """Test creating user without authentication"""
    user_data = {
        "email": "test@test.com",
        "password": "password",
        "full_name": "Test User",
        "role": UserRole.MANAGER.value
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_users(client, auth_headers_owner):
    """Test getting list of users"""
    response = client.get("/api/v1/users/", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_user_by_id(client, auth_headers_owner, test_owner_user):
    """Test getting user by ID"""
    response = client.get(
        f"/api/v1/users/{test_owner_user.id}",
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_owner_user.id
    assert data["email"] == test_owner_user.email


def test_get_user_not_found(client, auth_headers_owner):
    """Test getting non-existent user"""
    response = client.get("/api/v1/users/99999", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user(client, auth_headers_owner, test_owner_user):
    """Test updating user"""
    update_data = {
        "full_name": "Updated Name",
        "phone": "+9876543210"
    }
    response = client.put(
        f"/api/v1/users/{test_owner_user.id}",
        json=update_data,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["phone"] == update_data["phone"]

