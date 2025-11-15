"""
Tests for authentication endpoints
"""
import pytest
from fastapi import status


def test_login_success(client, test_owner_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_owner_user.email,
            "password": "testpassword"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_owner_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_owner_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@test.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers_owner, test_owner_user):
    """Test getting current user info"""
    response = client.get("/api/v1/auth/me", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_owner_user.email
    assert data["role"] == test_owner_user.role.value


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

