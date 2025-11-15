"""
Tests for product endpoints
"""
import pytest
from fastapi import status
from decimal import Decimal
from app.models.product import ProductUnit


def test_create_product(client, auth_headers_owner, test_supplier):
    """Test creating a product as owner"""
    product_data = {
        "supplier_id": test_supplier.id,
        "name": "Test Product",
        "description": "A test product",
        "price": "100.00",
        "stock_quantity": "50.00",
        "unit": ProductUnit.KILOGRAM.value,
        "min_order_quantity": "1.00"
    }
    response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["supplier_id"] == test_supplier.id


def test_create_product_unauthorized(client, test_supplier):
    """Test creating product without authentication"""
    product_data = {
        "supplier_id": test_supplier.id,
        "name": "Test Product",
        "price": "100.00"
    }
    response = client.post("/api/v1/products/", json=product_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_products(client, auth_headers_owner):
    """Test getting list of products"""
    response = client.get("/api/v1/products/", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_products_by_supplier(client, auth_headers_owner, test_supplier):
    """Test getting products filtered by supplier"""
    response = client.get(
        f"/api/v1/products/?supplier_id={test_supplier.id}",
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_product_by_id(client, auth_headers_owner, test_supplier):
    """Test getting product by ID"""
    # First create a product
    product_data = {
        "supplier_id": test_supplier.id,
        "name": "Test Product",
        "price": "100.00",
        "stock_quantity": "50.00",
        "unit": ProductUnit.KILOGRAM.value
    }
    create_response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=auth_headers_owner
    )
    assert create_response.status_code == status.HTTP_201_CREATED, f"Failed to create product: {create_response.status_code} - {create_response.text}"
    product_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == product_id


def test_update_product(client, auth_headers_owner, test_supplier):
    """Test updating product"""
    # First create a product
    product_data = {
        "supplier_id": test_supplier.id,
        "name": "Test Product",
        "price": "100.00",
        "stock_quantity": "50.00",
        "unit": ProductUnit.KILOGRAM.value
    }
    create_response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=auth_headers_owner
    )
    assert create_response.status_code == status.HTTP_201_CREATED, f"Failed to create product: {create_response.status_code} - {create_response.text}"
    product_id = create_response.json()["id"]
    
    # Then update it
    update_data = {
        "name": "Updated Product Name",
        "price": "150.00"
    }
    response = client.put(
        f"/api/v1/products/{product_id}",
        json=update_data,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]


def test_delete_product(client, auth_headers_owner, test_supplier):
    """Test deleting product"""
    # First create a product
    product_data = {
        "supplier_id": test_supplier.id,
        "name": "Test Product",
        "price": "100.00",
        "stock_quantity": "50.00",
        "unit": ProductUnit.KILOGRAM.value
    }
    create_response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=auth_headers_owner
    )
    assert create_response.status_code == status.HTTP_201_CREATED, f"Failed to create product: {create_response.status_code} - {create_response.text}"
    product_id = create_response.json()["id"]
    
    # Then delete it
    response = client.delete(
        f"/api/v1/products/{product_id}",
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    get_response = client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers_owner
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

