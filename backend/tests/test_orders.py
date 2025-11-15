"""
Tests for order endpoints
"""
import pytest
from fastapi import status
from decimal import Decimal
from app.models.order import OrderStatus
from app.models.product import ProductUnit


def test_create_order(client, auth_headers_consumer, test_supplier, test_consumer, db_session):
    """Test creating an order as consumer"""
    # First create a link
    from app.models.link import Link, LinkStatus
    link = Link(
        supplier_id=test_supplier.id,
        consumer_id=test_consumer.id,
        status=LinkStatus.ACCEPTED,
        requested_by_consumer=True
    )
    db_session.add(link)
    db_session.commit()
    
    # Create a product
    from app.models.product import Product
    product = Product(
        supplier_id=test_supplier.id,
        name="Test Product",
        price=Decimal("100.00"),
        stock_quantity=Decimal("50.00"),
        unit=ProductUnit.KILOGRAM,
        is_available=True,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Create order
    order_data = {
        "supplier_id": test_supplier.id,
        "consumer_id": test_consumer.id,
        "items": [
            {
                "product_id": product.id,
                "quantity": "10.00"
            }
        ],
        "delivery_method": "delivery",
        "notes": "Test order"
    }
    response = client.post(
        "/api/v1/orders/",
        json=order_data,
        headers=auth_headers_consumer
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == OrderStatus.PENDING.value
    assert len(data["items"]) == 1
    assert float(data["total"]) > 0


def test_create_order_without_link(client, auth_headers_consumer, test_supplier, test_consumer, db_session):
    """Test creating order without accepted link"""
    # Create a product
    from app.models.product import Product
    product = Product(
        supplier_id=test_supplier.id,
        name="Test Product",
        price=Decimal("100.00"),
        stock_quantity=Decimal("50.00"),
        unit=ProductUnit.KILOGRAM,
        is_available=True,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Try to create order without link
    order_data = {
        "supplier_id": test_supplier.id,
        "consumer_id": test_consumer.id,
        "items": [
            {
                "product_id": product.id,
                "quantity": "10.00"
            }
        ]
    }
    response = client.post(
        "/api/v1/orders/",
        json=order_data,
        headers=auth_headers_consumer
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_orders(client, auth_headers_owner):
    """Test getting list of orders"""
    response = client.get("/api/v1/orders/", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_update_order_status(client, auth_headers_owner, test_supplier, test_consumer, db_session):
    """Test updating order status (accept/reject)"""
    # Setup: create link, product, and order
    from app.models.link import Link, LinkStatus
    from app.models.product import Product
    from app.models.order import Order, OrderItem
    from decimal import Decimal
    
    link = Link(
        supplier_id=test_supplier.id,
        consumer_id=test_consumer.id,
        status=LinkStatus.ACCEPTED,
        requested_by_consumer=True
    )
    db_session.add(link)
    db_session.commit()
    
    product = Product(
        supplier_id=test_supplier.id,
        name="Test Product",
        price=Decimal("100.00"),
        stock_quantity=Decimal("50.00"),
        unit=ProductUnit.KILOGRAM,
        is_available=True,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    order = Order(
        supplier_id=test_supplier.id,
        consumer_id=test_consumer.id,
        order_number="ORD-TEST-001",
        status=OrderStatus.PENDING,
        subtotal=Decimal("1000.00"),
        total=Decimal("1000.00"),
        currency="KZT"
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    
    # Update order status
    update_data = {"status": OrderStatus.ACCEPTED.value}
    response = client.put(
        f"/api/v1/orders/{order.id}",
        json=update_data,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == OrderStatus.ACCEPTED.value

