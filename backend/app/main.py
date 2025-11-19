"""
Main FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.base import Base
from app.db.session import engine

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # Force reconfiguration
)
logger = logging.getLogger(__name__)
# Also configure root logger
logging.getLogger().setLevel(logging.INFO)

# Create database tables (only if they don't exist)
# This will fail if database is not available, but app will still start
try:
    # Base.metadata.create_all(bind=engine)
    pass
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")
    print("Make sure PostgreSQL is running and DATABASE_URL is correct")

app = FastAPI(
    title="Supplier Consumer Platform API",
    description="B2B platform for suppliers and institutional consumers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": False,
    },
)

# Request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else 'unknown'
        
        # Print to terminal (always visible)
        print(f"\n[REQUEST] {method} {path} from {client_host}")
        logger.info(f"Incoming request: {method} {path} from {client_host}")
        
        if path.startswith("/api/v1/auth"):
            print(f"[AUTH] Auth endpoint called: {method} {path}")
            logger.info(f"Auth endpoint called: {method} {path}")
        
        response = await call_next(request)
        
        print(f"[RESPONSE] {method} {path} -> {response.status_code}\n")
        logger.info(f"Response: {method} {path} -> {response.status_code}")
        
        return response

app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Supplier Consumer Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

