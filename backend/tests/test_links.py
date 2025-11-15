"""
Tests for link endpoints
"""
import pytest
from fastapi import status
from app.models.link import LinkStatus


def test_create_link_request(client, auth_headers_consumer, test_supplier, test_consumer):
    """Test creating a link request as consumer"""
    link_data = {
        "supplier_id": test_supplier.id,
        "consumer_id": test_consumer.id,
        "request_message": "Please accept my link request"
    }
    response = client.post(
        "/api/v1/links/",
        json=link_data,
        headers=auth_headers_consumer
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == LinkStatus.PENDING.value
    assert data["supplier_id"] == test_supplier.id
    assert data["consumer_id"] == test_consumer.id


def test_get_links(client, auth_headers_owner):
    """Test getting list of links"""
    response = client.get("/api/v1/links/", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_update_link_status(client, auth_headers_owner, test_supplier, test_consumer, db_session):
    """Test updating link status (approve/reject)"""
    # First create a link
    from app.models.link import Link
    link = Link(
        supplier_id=test_supplier.id,
        consumer_id=test_consumer.id,
        status=LinkStatus.PENDING,
        requested_by_consumer=True
    )
    db_session.add(link)
    db_session.commit()
    db_session.refresh(link)
    link_id = link.id
    
    # Then approve it
    update_data = {"status": LinkStatus.ACCEPTED.value}
    response = client.put(
        f"/api/v1/links/{link_id}",
        json=update_data,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == LinkStatus.ACCEPTED.value

