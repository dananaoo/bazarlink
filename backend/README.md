# Supplier Consumer Platform - Backend

FastAPI backend for the B2B Supplier Consumer Platform.

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   │   └── v1/
│   │       ├── endpoints/ # API endpoints
│   │       └── api.py    # Main API router
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings
│   │   ├── security.py   # Authentication utilities
│   │   └── dependencies.py # FastAPI dependencies
│   ├── db/               # Database configuration
│   │   ├── base.py       # Base model
│   │   └── session.py    # Database session
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py            # Alembic environment
├── alembic.ini           # Alembic configuration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker (optional, for containerized setup)

### Local Development

#### Option 1: Database in Docker, Backend locally (Recommended for development)

1. **Start PostgreSQL database with Docker**:
```bash
docker-compose up db -d
```

This will start only the PostgreSQL service on port 5432. Database credentials:
- Host: `localhost`
- Port: `5432`
- Database: `scp_db`
- User: `postgres`
- Password: `postgres`

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
# Create .env file with:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/scp_db
SECRET_KEY=your-secret-key-change-in-production
```

5. **Run the application**:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

#### Option 2: Everything in Docker

1. **Build and run with Docker Compose**:
```bash
docker-compose up --build
```

This will start:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000

#### Useful Docker Commands

**Start database only**:
```bash
docker-compose up db -d
```

**Stop database**:
```bash
docker-compose stop db
# or to remove container:
docker-compose down db
```

**View database logs**:
```bash
docker-compose logs -f db
```

**Access PostgreSQL shell**:
```bash
docker exec -it scp_postgres psql -U postgres -d scp_db
```

**Remove database volume (WARNING: deletes all data)**:
```bash
docker-compose down -v
```

**Start everything (database + backend)**:
```bash
docker-compose up -d
```

**Stop everything**:
```bash
docker-compose down
```

## Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations.

### Quick Commands

**Check current migration status**:
```bash
make migrate-current
# or
alembic current
```

**View migration history**:
```bash
make migrate-history
# or
alembic history
```

**Create a new migration** (after modifying models):
```bash
make migrate-create MESSAGE="add new field to user table"
# or
alembic revision --autogenerate -m "add new field to user table"
```

**Apply pending migrations**:
```bash
make migrate-upgrade
# or
alembic upgrade head
```

**Rollback one migration**:
```bash
make migrate-downgrade REVISION="-1"
# or
alembic downgrade -1
```

### Workflow

1. **Modify models** in `app/models/`
2. **Create migration**: `alembic revision --autogenerate -m "description"`
3. **Review** the generated migration file in `alembic/versions/`
4. **Apply migration**: `alembic upgrade head`
5. **Test** your changes

For detailed information, see [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md).

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

### Users
- `POST /api/v1/users/` - Create user (Owner only)
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user

### Suppliers
- `POST /api/v1/suppliers/` - Create supplier
- `GET /api/v1/suppliers/` - List suppliers
- `GET /api/v1/suppliers/{id}` - Get supplier by ID
- `PUT /api/v1/suppliers/{id}` - Update supplier

### Consumers
- `POST /api/v1/consumers/` - Create consumer
- `GET /api/v1/consumers/` - List consumers
- `GET /api/v1/consumers/{id}` - Get consumer by ID
- `PUT /api/v1/consumers/{id}` - Update consumer

### Products
- `POST /api/v1/products/` - Create product (Owner/Manager only)
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/{id}` - Get product by ID
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Links
- `POST /api/v1/links/` - Create link request
- `GET /api/v1/links/` - List links
- `GET /api/v1/links/{id}` - Get link by ID
- `PUT /api/v1/links/{id}` - Update link (approve/reject)

### Orders
- `POST /api/v1/orders/` - Create order (Consumer only)
- `GET /api/v1/orders/` - List orders
- `GET /api/v1/orders/{id}` - Get order by ID
- `PUT /api/v1/orders/{id}` - Update order (accept/reject)

## Testing Endpoints with Authorization

Most endpoints require authentication. Here's how to test them in FastAPI docs:

### Quick Start

1. **Get a token** using the login endpoint:
   - Go to `POST /api/v1/auth/login` in the docs
   - Click "Try it out"
   - Enter:
     - `username`: `admin@test.com` (your email)
     - `password`: `admin123`
   - Click "Execute"
   - Copy the `access_token` from the response

2. **Authorize in Swagger UI**:
   - Click the **"Authorize"** button (🔒 lock icon, top right)
   - In the OAuth2 modal, you'll see these fields:
     - **username**: Enter `admin@test.com` (your email)
     - **password**: Enter `admin123`
     - **client_id**: Leave empty (not needed for password flow)
     - **client_secret**: Leave empty (not needed for password flow)
   - Click "Authorize"
   - Close the modal

3. **Test protected endpoints**:
   - All endpoints with a 🔒 lock icon now work automatically
   - Your token is included in requests automatically

### Alternative: Direct Token Entry

If you already have a token:

1. Click "Authorize" button
2. Look for the "Value" or token input field
3. Paste: `Bearer <your_access_token>`
4. Click "Authorize"

### Test User Credentials

After running database initialization (`init_db.py`), you can use:

- **Email**: `admin@test.com`
- **Password**: `admin123`
- **Role**: `owner`

See `AUTH_GUIDE.md` for detailed authentication instructions.

## User Roles

- **CONSUMER**: Can request links, place orders, view catalog
- **OWNER**: Full control over supplier account
- **MANAGER**: Handles catalog, inventory, orders, escalations
- **SALES_REPRESENTATIVE**: Handles consumer communication, first-line complaints

## Database Models

- User
- Supplier
- Consumer
- Product
- Link (supplier-consumer relationship)
- Order
- OrderItem
- Complaint
- Incident
- Message

## Development Notes

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Implement proper error handling
- Use Pydantic schemas for request/response validation
- Follow RESTful API conventions

## Next Steps

- Set up Alembic for database migrations
- Add comprehensive error handling
- Implement complaint and incident endpoints
- Add message/chat endpoints
- Add unit and integration tests
- Implement rate limiting
- Add logging configuration

