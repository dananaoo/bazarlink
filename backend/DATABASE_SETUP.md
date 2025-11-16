# Database Setup Guide

## Quick Setup

### 1. Start Database
```bash
docker-compose up db -d
```

### 2. Initialize Database (Run inside Docker)
```bash
docker exec scp_backend python scripts/init_db.py
```

This creates:
- ✅ All database tables
- ✅ Test user: `admin@test.com` / `admin123` (role: owner)

### 3. Start Backend

**Option A: In Docker (Recommended)**
```bash
docker-compose up backend -d
```

**Option B: Locally**
```bash
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

## Database Tables

The following tables are created:
- `users` - User accounts
- `suppliers` - Supplier companies
- `consumers` - Consumer companies (restaurants/hotels)
- `products` - Product catalog
- `links` - Supplier-consumer relationships
- `orders` - Orders
- `order_items` - Order line items
- `complaints` - Complaints/disputes
- `incidents` - Incidents
- `messages` - Messages

## Test User

After initialization, you can login with:
- **Email**: `admin@test.com`
- **Password**: `admin123`
- **Role**: `owner`

## API Endpoints

### Base URL
- Local: `http://localhost:8000`
- Docker: `http://localhost:8000`

### Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoint Groups

1. **Authentication** (`/api/v1/auth`)
   - `POST /login` - Login (public)
   - `GET /me` - Get current user (requires auth)

2. **Users** (`/api/v1/users`)
   - `POST /` - Create user (Owner only)
   - `GET /` - List users
   - `GET /{id}` - Get user
   - `PUT /{id}` - Update user

3. **Suppliers** (`/api/v1/suppliers`)
   - `POST /` - Create supplier (public)
   - `GET /` - List suppliers
   - `GET /{id}` - Get supplier
   - `PUT /{id}` - Update supplier

4. **Consumers** (`/api/v1/consumers`)
   - `POST /` - Create consumer (public)
   - `GET /` - List consumers
   - `GET /{id}` - Get consumer
   - `PUT /{id}` - Update consumer

5. **Products** (`/api/v1/products`)
   - `POST /` - Create product (Owner/Manager only)
   - `GET /` - List products
   - `GET /{id}` - Get product
   - `PUT /{id}` - Update product

6. **Links** (`/api/v1/links`)
   - `POST /` - Create link request
   - `GET /` - List links
   - `GET /{id}` - Get link
   - `PUT /{id}` - Update link status

7. **Orders** (`/api/v1/orders`)
   - `POST /` - Create order
   - `GET /` - List orders
   - `GET /{id}` - Get order
   - `PUT /{id}` - Update order status

## Testing in FastAPI Docs

1. Open `http://localhost:8000/docs`
2. Use `POST /api/v1/auth/login`:
   - `username`: `admin@test.com`
   - `password`: `admin123`
3. Copy the `access_token` from response
4. Click **"Authorize"** button (top right)
5. Paste token: `Bearer <token>` (or just the token)
6. Click "Authorize"
7. Test all protected endpoints! 🔒

## Troubleshooting

### Tables not created?
```bash
docker exec scp_backend python scripts/init_db.py
```

### Can't connect to database?
- Check Docker: `docker ps | grep scp_postgres`
- Check logs: `docker logs scp_postgres`
- Verify connection: `docker exec scp_postgres psql -U postgres -d scp_db -c "SELECT 1;"`

### Backend not starting?
- Check logs: `docker logs scp_backend`
- Rebuild: `docker-compose up backend --build -d`

### Login returns 500 error?
- Verify user exists: `docker exec scp_postgres psql -U postgres -d scp_db -c "SELECT * FROM users;"`
- Re-run init: `docker exec scp_backend python scripts/init_db.py`

