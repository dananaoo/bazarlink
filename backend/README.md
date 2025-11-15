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

