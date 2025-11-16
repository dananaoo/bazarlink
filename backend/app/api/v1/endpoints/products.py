"""
Product endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import UserRole
from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.product import Product as ProductSchema, ProductCreate, ProductUpdate

router = APIRouter()


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new product (Owner/Manager only)"""
    if current_user.role not in [UserRole.OWNER, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Verify supplier exists
    supplier = db.query(Supplier).filter(Supplier.id == product_in.supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Verify user has access to this supplier
    if current_user.supplier_id != product_in.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create products for your own supplier"
        )
    
    # If category_id is provided, verify it belongs to the same supplier
    if product_in.category_id:
        from app.models.category import Category
        category = db.query(Category).filter(Category.id == product_in.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        if category.supplier_id != product_in.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category does not belong to this supplier"
            )
    
    db_product = Product(**product_in.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.get("/", response_model=List[ProductSchema])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    supplier_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of products"""
    from app.models.link import Link, LinkStatus
    
    query = db.query(Product)
    
    # Consumers can only see products from suppliers they have ACCEPTED links with
    if current_user.role == UserRole.CONSUMER:
        if not current_user.consumer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Consumer profile not found"
            )
        
        # Get all accepted links for this consumer
        accepted_links = db.query(Link).filter(
            Link.consumer_id == current_user.consumer_id,
            Link.status == LinkStatus.ACCEPTED
        ).all()
        
        accepted_supplier_ids = [link.supplier_id for link in accepted_links]
        
        if not accepted_supplier_ids:
            # Consumer has no accepted links, return empty
            return []
        
        # Filter products by accepted suppliers
        query = query.filter(Product.supplier_id.in_(accepted_supplier_ids))
        
        # If supplier_id specified, verify it's in accepted list
        if supplier_id and supplier_id not in accepted_supplier_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have an accepted link with this supplier"
            )
    elif current_user.role in [UserRole.OWNER, UserRole.MANAGER, UserRole.SALES_REPRESENTATIVE]:
        # Supplier staff can see all products for their supplier
        if current_user.supplier_id:
            query = query.filter(Product.supplier_id == current_user.supplier_id)
    
    if supplier_id:
        query = query.filter(Product.supplier_id == supplier_id)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get product by ID"""
    from app.models.link import Link, LinkStatus
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Consumers can only see products from suppliers they have ACCEPTED links with
    if current_user.role == UserRole.CONSUMER:
        if not current_user.consumer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Consumer profile not found"
            )
        
        # Check if consumer has accepted link with this supplier
        link = db.query(Link).filter(
            Link.consumer_id == current_user.consumer_id,
            Link.supplier_id == product.supplier_id,
            Link.status == LinkStatus.ACCEPTED
        ).first()
        
        if not link:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have an accepted link with this supplier"
            )
    elif current_user.role in [UserRole.OWNER, UserRole.MANAGER, UserRole.SALES_REPRESENTATIVE]:
        # Supplier staff can only see products for their supplier
        if current_user.supplier_id and product.supplier_id != current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update product (Owner/Manager only)"""
    if current_user.role not in [UserRole.OWNER, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Verify user has access to this supplier
    if current_user.supplier_id != product.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update products for your own supplier"
        )
    
    # If category_id is being updated, verify it belongs to the same supplier
    if product_in.category_id is not None and product_in.category_id != product.category_id:
        from app.models.category import Category
        if product_in.category_id:  # If not None (could be None to remove category)
            category = db.query(Category).filter(Category.id == product_in.category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
            if category.supplier_id != product.supplier_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category does not belong to this supplier"
                )
    
    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete product (Owner/Manager only)"""
    if current_user.role not in [UserRole.OWNER, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    
    return None

