"""
Order endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from decimal import Decimal
from app.core.dependencies import get_db, get_current_user
from app.models.user import UserRole
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import Order as OrderSchema, OrderCreate, OrderUpdate

router = APIRouter()


def generate_order_number() -> str:
    """Generate unique order number"""
    return f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{datetime.utcnow().microsecond}"


@router.post("/", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new order (Consumer only)"""
    if current_user.role != UserRole.CONSUMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers can create orders"
        )
    
    # Verify consumer has accepted link with supplier
    from app.models.link import Link, LinkStatus
    link = db.query(Link).filter(
        Link.supplier_id == order_in.supplier_id,
        Link.consumer_id == order_in.consumer_id,
        Link.status == LinkStatus.ACCEPTED
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consumer must have an accepted link with supplier to place orders"
        )
    
    # Calculate totals
    subtotal = Decimal("0")
    items_data = []
    
    for item in order_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )
        
        if not product.is_available or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.name} is not available"
            )
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.name}"
            )
        
        unit_price = product.discount_price if product.discount_price else product.price
        total_price = unit_price * item.quantity
        subtotal += total_price
        
        items_data.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "total_price": total_price
        })
    
    total = subtotal  # Can add taxes, shipping, etc. here
    
    # Create order
    db_order = Order(
        supplier_id=order_in.supplier_id,
        consumer_id=order_in.consumer_id,
        order_number=generate_order_number(),
        status=OrderStatus.PENDING,
        delivery_method=order_in.delivery_method,
        delivery_address=order_in.delivery_address,
        delivery_date=order_in.delivery_date,
        notes=order_in.notes,
        subtotal=subtotal,
        total=total,
        currency="KZT"
    )
    
    db.add(db_order)
    db.flush()
    
    # Create order items
    for item_data in items_data:
        db_item = OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    
    # Load items
    db_order.items  # Trigger lazy loading
    return db_order


@router.get("/", response_model=List[OrderSchema])
async def get_orders(
    supplier_id: int = None,
    consumer_id: int = None,
    status: OrderStatus = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of orders"""
    query = db.query(Order)
    
    # Role-based filtering
    if current_user.role == UserRole.CONSUMER:
        query = query.filter(Order.consumer_id == current_user.consumer_id)
    elif current_user.role in [UserRole.OWNER, UserRole.MANAGER, UserRole.SALES_REPRESENTATIVE]:
        query = query.filter(Order.supplier_id == current_user.supplier_id)
    
    if supplier_id:
        query = query.filter(Order.supplier_id == supplier_id)
    if consumer_id:
        query = query.filter(Order.consumer_id == consumer_id)
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    # Load items for each order
    for order in orders:
        order.items  # Trigger lazy loading
    return orders


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.CONSUMER and order.consumer_id != current_user.consumer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if current_user.role in [UserRole.OWNER, UserRole.MANAGER, UserRole.SALES_REPRESENTATIVE]:
        if order.supplier_id != current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Load items
    order.items  # Trigger lazy loading
    return order


@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(
    order_id: int,
    order_in: OrderUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update order (Supplier Owner/Manager can accept/reject)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Only suppliers can accept/reject orders
    if order_in.status and order_in.status != order.status:
        if current_user.role not in [UserRole.OWNER, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and managers can accept/reject orders"
            )
        
        order.status = order_in.status
        if order_in.status == OrderStatus.ACCEPTED:
            order.accepted_at = datetime.utcnow()
        elif order_in.status == OrderStatus.COMPLETED:
            order.completed_at = datetime.utcnow()
    else:
        update_data = order_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete order (Consumer can only delete their own orders if status is PENDING)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Only consumers can delete orders
    if current_user.role != UserRole.CONSUMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers can delete orders"
        )
    
    # Consumer can only delete their own orders
    if order.consumer_id != current_user.consumer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own orders"
        )
    
    # Consumer can only delete orders that are not accepted yet
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete order with status '{order.status}'. Only pending orders can be deleted."
        )
    
    # Delete the order (cascade will delete order items)
    db.delete(order)
    db.commit()
    
    return None

