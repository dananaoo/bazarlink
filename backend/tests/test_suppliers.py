"""
Tests for supplier endpoints
"""
import pytest
from fastapi import status


def test_create_supplier(client):
    """Test creating a supplier"""
    supplier_data = {
        "company_name": "New Supplier",
        "legal_name": "New Supplier LLC",
        "email": "newsupplier@test.com",
        "phone": "+1234567893",
        "city": "Almaty",
        "country": "KZ"
    }
    response = client.post("/api/v1/suppliers/", json=supplier_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["company_name"] == supplier_data["company_name"]
    assert data["email"] == supplier_data["email"]


def test_create_supplier_duplicate_email(client, test_supplier):
    """Test creating supplier with duplicate email"""
    supplier_data = {
        "company_name": "Duplicate Supplier",
        "email": test_supplier.email,
        "city": "Almaty",
        "country": "KZ"
    }
    response = client.post("/api/v1/suppliers/", json=supplier_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_suppliers(client, auth_headers_owner):
    """Test getting list of suppliers"""
    response = client.get("/api/v1/suppliers/", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_supplier_by_id(client, auth_headers_owner, test_supplier):
    """Test getting supplier by ID"""
    response = client.get(
        f"/api/v1/suppliers/{test_supplier.id}",
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_supplier.id
    assert data["company_name"] == test_supplier.company_name


def test_get_supplier_not_found(client, auth_headers_owner):
    """Test getting non-existent supplier"""
    response = client.get("/api/v1/suppliers/99999", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_supplier(client, auth_headers_owner, test_supplier):
    """Test updating supplier"""
    update_data = {
        "company_name": "Updated Supplier Name",
        "phone": "+9876543211"
    }
    response = client.put(
        f"/api/v1/suppliers/{test_supplier.id}",
        json=update_data,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["company_name"] == update_data["company_name"]
    assert data["phone"] == update_data["phone"]

