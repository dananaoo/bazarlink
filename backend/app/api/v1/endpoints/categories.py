"""
Category endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import UserRole
from app.models.category import Category
from app.models.supplier import Supplier
from app.schemas.category import Category as CategorySchema, CategoryCreate, CategoryUpdate

router = APIRouter()


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new category (Owner/Manager only)"""
    if current_user.role not in [UserRole.OWNER, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Verify supplier exists
    supplier = db.query(Supplier).filter(Supplier.id == category_in.supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Verify user has access to this supplier
    if current_user.supplier_id != category_in.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create categories for your own supplier"
        )
    
    # Check if category with same name already exists for this supplier
    existing_category = db.query(Category).filter(
        Category.supplier_id == category_in.supplier_id,
        Category.name == category_in.name
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists for this supplier"
        )
    
    db_category = Category(**category_in.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.get("/", response_model=List[CategorySchema])
async def get_categories(
    supplier_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of categories"""
    from app.models.link import Link, LinkStatus
    
    query = db.query(Category)
    
    # Consumers can only see categories from suppliers they have ACCEPTED links with
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
        
        # Filter categories by accepted suppliers
        query = query.filter(Category.supplier_id.in_(accepted_supplier_ids))
        
        # If supplier_id specified, verify it's in accepted list
        if supplier_id and supplier_id not in accepted_supplier_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have an accepted link with this supplier"
            )
    elif current_user.role in [UserRole.OWNER, UserRole.MANAGER, UserRole.SALES_REPRESENTATIVE]:
        # Supplier staff can see all categories for their supplier
        if current_user.supplier_id:
            query = query.filter(Category.supplier_id == current_user.supplier_id)
    
    if supplier_id:
        query = query.filter(Category.supplier_id == supplier_id)
    
    # Filter only active categories and order by name
    query = query.filter(Category.is_active == True)
    categories = query.order_by(Category.name).all()
    
    return categories


@router.get("/{category_id}", response_model=CategorySchema)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get category by ID"""
    from app.models.link import Link, LinkStatus
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Consumers can only see categories from suppliers they have ACCEPTED links with
    if current_user.role == UserRole.CONSUMER:
        if not current_user.consumer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Consumer profile not found"
            )
        
        # Check if consumer has accepted link with this supplier
        link = db.query(Link).filter(
            Link.consumer_id == current_user.consumer_id,
            Link.supplier_id == category.supplier_id,
            Link.status == LinkStatus.ACCEPTED
        ).first()
        
        if not link:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have an accepted link with this supplier"
            )
    elif current_user.role in [UserRole.OWNER, UserRole.MANAGER, UserRole.SALES_REPRESENTATIVE]:
        # Supplier staff can only see categories for their supplier
        if current_user.supplier_id and category.supplier_id != current_user.supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update category (Owner/Manager only)"""
    if current_user.role not in [UserRole.OWNER, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Verify user has access to this supplier
    if current_user.supplier_id != category.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update categories for your own supplier"
        )
    
    # If name is being updated, check for duplicates
    if category_in.name and category_in.name != category.name:
        existing_category = db.query(Category).filter(
            Category.supplier_id == category.supplier_id,
            Category.name == category_in.name,
            Category.id != category_id
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists for this supplier"
            )
    
    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete category (Owner/Manager only)"""
    if current_user.role not in [UserRole.OWNER, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Verify user has access to this supplier
    if current_user.supplier_id != category.supplier_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete categories for your own supplier"
        )
    
    # Check if category has products
    if category.products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category. It has {len(category.products)} product(s). Please move or delete products first."
        )
    
    db.delete(category)
    db.commit()
    
    return None

