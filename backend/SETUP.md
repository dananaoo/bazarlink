# Backend Setup Guide

## Quick Start

### 1. Start Database

```bash
# Start PostgreSQL in Docker
docker-compose up db -d

# Verify it's running
docker ps | grep scp_postgres
```

### 2. Initialize Database

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Linux/Mac

# Run database initialization
python scripts/init_db.py
```

This will:
- Create all database tables
- Create a test user (admin@test.com / admin123)

### 3. Start FastAPI Server

**Option A: Run locally (if database connection works)**
```bash
uvicorn app.main:app --reload
```

**Option B: Run in Docker (recommended if local connection fails)**
```bash
docker-compose up backend -d
```

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints Overview

### Authentication (`/api/v1/auth`)
- `POST /login` - User login (returns JWT token)
- `GET /me` - Get current user info (requires auth)

### Users (`/api/v1/users`)
- `POST /` - Create user (Owner only, requires auth)
- `GET /` - List users (requires auth)
- `GET /{id}` - Get user by ID (requires auth)
- `PUT /{id}` - Update user (requires auth)

### Suppliers (`/api/v1/suppliers`)
- `POST /` - Create supplier (public)
- `GET /` - List suppliers (requires auth)
- `GET /{id}` - Get supplier by ID (requires auth)
- `PUT /{id}` - Update supplier (requires auth)

### Consumers (`/api/v1/consumers`)
- `POST /` - Create consumer (public)
- `GET /` - List consumers (requires auth)
- `GET /{id}` - Get consumer by ID (requires auth)
- `PUT /{id}` - Update consumer (requires auth)

### Products (`/api/v1/products`)
- `POST /` - Create product (Owner/Manager only, requires auth)
- `GET /` - List products (requires auth)
- `GET /{id}` - Get product by ID (requires auth)
- `PUT /{id}` - Update product (Owner/Manager only, requires auth)

### Links (`/api/v1/links`)
- `POST /` - Create link request (requires auth)
- `GET /` - List links (requires auth)
- `GET /{id}` - Get link by ID (requires auth)
- `PUT /{id}` - Update link status (requires auth)

### Orders (`/api/v1/orders`)
- `POST /` - Create order (requires auth)
- `GET /` - List orders (requires auth)
- `GET /{id}` - Get order by ID (requires auth)
- `PUT /{id}` - Update order status (requires auth)

## Testing Endpoints

### 1. Get Access Token

In FastAPI docs (`/docs`):
1. Find `POST /api/v1/auth/login`
2. Click "Try it out"
3. Enter:
   - `username`: `admin@test.com`
   - `password`: `admin123`
4. Click "Execute"
5. Copy the `access_token` from response

### 2. Authorize in FastAPI Docs

1. Click the **"Authorize"** button (top right, lock icon)
2. In the authorization modal:
   - Find `oauth2_scheme` or `Bearer`
   - Enter: `Bearer <your_access_token>` (or just paste the token)
3. Click "Authorize", then "Close"

### 3. Test Protected Endpoints

All endpoints with a 🔒 icon now use your token automatically!

## Database Connection Issues

If you get connection errors when running locally:

### Solution 1: Use Docker for Backend
```bash
docker-compose up backend -d
```

### Solution 2: Check Database URL
Make sure your `.env` file has:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/scp_db
```

### Solution 3: Verify Database is Running
```bash
docker ps | grep scp_postgres
docker exec scp_postgres psql -U postgres -d scp_db -c "SELECT 1;"
```

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/scp_db

# Security
SECRET_KEY=your-secret-key-change-in-production-use-strong-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
```

## Troubleshooting

### Tables not created?
Run: `python scripts/init_db.py`

### Can't connect to database?
1. Check Docker: `docker ps`
2. Check database logs: `docker logs scp_postgres`
3. Try connecting: `docker exec scp_postgres psql -U postgres -d scp_db`

### Login returns 500 error?
1. Check if user exists: `docker exec scp_postgres psql -U postgres -d scp_db -c "SELECT * FROM users;"`
2. Re-run init script: `python scripts/init_db.py`
3. Check server logs for detailed error

