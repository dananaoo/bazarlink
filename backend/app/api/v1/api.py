"""
Main API router for v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, suppliers, consumers, products, links, orders

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(consumers.router, prefix="/consumers", tags=["consumers"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(links.router, prefix="/links", tags=["links"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])

