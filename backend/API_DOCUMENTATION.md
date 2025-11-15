# Supplier Consumer Platform API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

To obtain a token, use the login endpoint.

---

## Endpoints

### Authentication

#### POST `/auth/login`
User login endpoint.

**Request:**
- Content-Type: `application/x-www-form-urlencoded`
- Body:
  - `username`: User email (string, required)
  - `password`: User password (string, required)

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK`: Login successful
- `401 UNAUTHORIZED`: Invalid credentials
- `403 FORBIDDEN`: User account is inactive

---

#### GET `/auth/me`
Get current authenticated user information.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "role": "owner",
  "is_active": true,
  "language": "en",
  "supplier_id": 1,
  "consumer_id": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

**Status Codes:**
- `200 OK`: Success
- `401 UNAUTHORIZED`: Missing or invalid token

---

### Users

#### POST `/users/`
Create a new user (Owner only).

**Headers:**
- `Authorization: Bearer <token>` (required, Owner role)

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "full_name": "New User",
  "phone": "+1234567890",
  "role": "manager",
  "language": "en"
}
```

**Response:**
```json
{
  "id": 2,
  "email": "newuser@example.com",
  "full_name": "New User",
  "role": "manager",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `201 CREATED`: User created successfully
- `400 BAD REQUEST`: User with email already exists
- `401 UNAUTHORIZED`: Not authenticated
- `403 FORBIDDEN`: Insufficient permissions (not Owner)

---

#### GET `/users/`
Get list of users.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "owner",
    "is_active": true
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `401 UNAUTHORIZED`: Not authenticated

---

#### GET `/users/{user_id}`
Get user by ID.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Path Parameters:**
- `user_id`: User ID (integer, required)

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "owner",
  "is_active": true
}
```

**Status Codes:**
- `200 OK`: Success
- `404 NOT FOUND`: User not found
- `401 UNAUTHORIZED`: Not authenticated

---

#### PUT `/users/{user_id}`
Update user information.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Path Parameters:**
- `user_id`: User ID (integer, required)

**Request Body:**
```json
{
  "full_name": "Updated Name",
  "phone": "+9876543210",
  "language": "ru",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Updated Name",
  "phone": "+9876543210",
  "role": "owner",
  "is_active": true
}
```

**Status Codes:**
- `200 OK`: User updated successfully
- `404 NOT FOUND`: User not found
- `401 UNAUTHORIZED`: Not authenticated

---

### Suppliers

#### POST `/suppliers/`
Create a new supplier.

**Request Body:**
```json
{
  "company_name": "ABC Foods",
  "legal_name": "ABC Foods LLC",
  "tax_id": "123456789",
  "email": "info@abcfoods.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "Almaty",
  "country": "KZ",
  "description": "Food supplier",
  "website": "https://abcfoods.com"
}
```

**Response:**
```json
{
  "id": 1,
  "company_name": "ABC Foods",
  "email": "info@abcfoods.com",
  "verification_status": "pending",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `201 CREATED`: Supplier created successfully
- `400 BAD REQUEST`: Supplier with email already exists

---

#### GET `/suppliers/`
Get list of suppliers.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "company_name": "ABC Foods",
    "email": "info@abcfoods.com",
    "verification_status": "verified",
    "is_active": true
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `401 UNAUTHORIZED`: Not authenticated

---

#### GET `/suppliers/{supplier_id}`
Get supplier by ID.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Path Parameters:**
- `supplier_id`: Supplier ID (integer, required)

**Response:**
```json
{
  "id": 1,
  "company_name": "ABC Foods",
  "email": "info@abcfoods.com",
  "verification_status": "verified",
  "is_active": true
}
```

**Status Codes:**
- `200 OK`: Success
- `404 NOT FOUND`: Supplier not found
- `401 UNAUTHORIZED`: Not authenticated

---

#### PUT `/suppliers/{supplier_id}`
Update supplier information (Owner/Manager only).

**Headers:**
- `Authorization: Bearer <token>` (required, Owner or Manager role)

**Path Parameters:**
- `supplier_id`: Supplier ID (integer, required)

**Request Body:**
```json
{
  "company_name": "Updated Company Name",
  "phone": "+9876543210",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "id": 1,
  "company_name": "Updated Company Name",
  "phone": "+9876543210",
  "is_active": true
}
```

**Status Codes:**
- `200 OK`: Supplier updated successfully
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT FOUND`: Supplier not found
- `401 UNAUTHORIZED`: Not authenticated

---

### Consumers

#### POST `/consumers/`
Create a new consumer.

**Request Body:**
```json
{
  "business_name": "Restaurant XYZ",
  "legal_name": "Restaurant XYZ LLC",
  "tax_id": "987654321",
  "email": "info@restaurantxyz.com",
  "phone": "+1234567891",
  "address": "456 Food St",
  "city": "Almaty",
  "country": "KZ",
  "business_type": "restaurant",
  "description": "Fine dining restaurant"
}
```

**Response:**
```json
{
  "id": 1,
  "business_name": "Restaurant XYZ",
  "email": "info@restaurantxyz.com",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `201 CREATED`: Consumer created successfully
- `400 BAD REQUEST`: Consumer with email already exists

---

#### GET `/consumers/`
Get list of consumers.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "business_name": "Restaurant XYZ",
    "email": "info@restaurantxyz.com",
    "is_active": true
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `401 UNAUTHORIZED`: Not authenticated

---

#### GET `/consumers/{consumer_id}`
Get consumer by ID.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Path Parameters:**
- `consumer_id`: Consumer ID (integer, required)

**Response:**
```json
{
  "id": 1,
  "business_name": "Restaurant XYZ",
  "email": "info@restaurantxyz.com",
  "is_active": true
}
```

**Status Codes:**
- `200 OK`: Success
- `404 NOT FOUND`: Consumer not found
- `401 UNAUTHORIZED`: Not authenticated

---

#### PUT `/consumers/{consumer_id}`
Update consumer information.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Path Parameters:**
- `consumer_id`: Consumer ID (integer, required)

**Request Body:**
```json
{
  "business_name": "Updated Restaurant Name",
  "phone": "+9876543211"
}
```

**Response:**
```json
{
  "id": 1,
  "business_name": "Updated Restaurant Name",
  "phone": "+9876543211",
  "is_active": true
}
```

**Status Codes:**
- `200 OK`: Consumer updated successfully
- `404 NOT FOUND`: Consumer not found
- `401 UNAUTHORIZED`: Not authenticated

---

### Products

#### POST `/products/`
Create a new product (Owner/Manager only).

**Headers:**
- `Authorization: Bearer <token>` (required, Owner or Manager role)

**Request Body:**
```json
{
  "supplier_id": 1,
  "name": "Premium Beef",
  "description": "High quality beef",
  "sku": "BEEF-001",
  "category": "Meat",
  "price": "5000.00",
  "discount_price": "4500.00",
  "currency": "KZT",
  "stock_quantity": "100.00",
  "unit": "kg",
  "min_order_quantity": "1.00",
  "delivery_available": true,
  "pickup_available": true,
  "lead_time_days": 2
}
```

**Response:**
```json
{
  "id": 1,
  "supplier_id": 1,
  "name": "Premium Beef",
  "price": "5000.00",
  "stock_quantity": "100.00",
  "unit": "kg",
  "is_available": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `201 CREATED`: Product created successfully
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT FOUND`: Supplier not found
- `401 UNAUTHORIZED`: Not authenticated

---

#### GET `/products/`
Get list of products.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)
- `supplier_id`: Filter by supplier ID (integer, optional)

**Response:**
```json
[
  {
    "id": 1,
    "supplier_id": 1,
    "name": "Premium Beef",
    "price": "5000.00",
    "stock_quantity": "100.00",
    "unit": "kg",
    "is_available": true
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `401 UNAUTHORIZED`: Not authenticated

---

#### GET `/products/{product_id}`
Get product by ID.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Path Parameters:**
- `product_id`: Product ID (integer, required)

**Response:**
```json
{
  "id": 1,
  "supplier_id": 1,
  "name": "Premium Beef",
  "price": "5000.00",
  "stock_quantity": "100.00",
  "unit": "kg",
  "is_available": true
}
```

**Status Codes:**
- `200 OK`: Success
- `404 NOT FOUND`: Product not found
- `401 UNAUTHORIZED`: Not authenticated

---

#### PUT `/products/{product_id}`
Update product information (Owner/Manager only).

**Headers:**
- `Authorization: Bearer <token>` (required, Owner or Manager role)

**Path Parameters:**
- `product_id`: Product ID (integer, required)

**Request Body:**
```json
{
  "name": "Updated Product Name",
  "price": "5500.00",
  "stock_quantity": "150.00",
  "is_available": true
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Updated Product Name",
  "price": "5500.00",
  "stock_quantity": "150.00",
  "is_available": true
}
```

**Status Codes:**
- `200 OK`: Product updated successfully
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT FOUND`: Product not found
- `401 UNAUTHORIZED`: Not authenticated

---

#### DELETE `/products/{product_id}`
Delete a product (Owner/Manager only).

**Headers:**
- `Authorization: Bearer <token>` (required, Owner or Manager role)

**Path Parameters:**
- `product_id`: Product ID (integer, required)

**Status Codes:**
- `204 NO CONTENT`: Product deleted successfully
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT FOUND`: Product not found
- `401 UNAUTHORIZED`: Not authenticated

---

### Links

#### POST `/links/`
Create a link request between supplier and consumer.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Request Body:**
```json
{
  "supplier_id": 1,
  "consumer_id": 1,
  "request_message": "Please accept my link request"
}
```

**Response:**
```json
{
  "id": 1,
  "supplier_id": 1,
  "consumer_id": 1,
  "status": "pending",
  "requested_by_consumer": true,
  "request_message": "Please accept my link request",
  "requested_at": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `201 CREATED`: Link request created successfully
- `400 BAD REQUEST`: Link already exists
- `401 UNAUTHORIZED`: Not authenticated

---

#### GET `/links/`
Get list of links.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)
- `supplier_id`: Filter by supplier ID (integer, optional)
- `consumer_id`: Filter by consumer ID (integer, optional)
- `status`: Filter by status - `pending`, `accepted`, `removed`, `blocked` (string, optional)

**Response:**
```json
[
  {
    "id": 1,
    "supplier_id": 1,
    "consumer_id": 1,
    "status": "accepted",
    "requested_by_consumer": true,
    "requested_at": "2024-01-01T00:00:00Z"
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `401 UNAUTHORIZED`: Not authenticated

---

#### GET `/links/{link_id}`
Get link by ID.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Path Parameters:**
- `link_id`: Link ID (integer, required)

**Response:**
```json
{
  "id": 1,
  "supplier_id": 1,
  "consumer_id": 1,
  "status": "accepted",
  "requested_by_consumer": true,
  "requested_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `404 NOT FOUND`: Link not found
- `401 UNAUTHORIZED`: Not authenticated

---

#### PUT `/links/{link_id}`
Update link status (approve/reject) - Supplier Owner/Manager only.

**Headers:**
- `Authorization: Bearer <token>` (required, Owner or Manager role)

**Path Parameters:**
- `link_id`: Link ID (integer, required)

**Request Body:**
```json
{
  "status": "accepted"
}
```

**Status Values:**
- `pending`: Initial status
- `accepted`: Link approved
- `removed`: Link removed
- `blocked`: Link blocked

**Response:**
```json
{
  "id": 1,
  "supplier_id": 1,
  "consumer_id": 1,
  "status": "accepted",
  "responded_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Link updated successfully
- `403 FORBIDDEN`: Insufficient permissions (only suppliers can approve/reject)
- `404 NOT FOUND`: Link not found
- `401 UNAUTHORIZED`: Not authenticated

---

### Orders

#### POST `/orders/`
Create a new order (Consumer only, requires accepted link).

**Headers:**
- `Authorization: Bearer <token>` (required, Consumer role)

**Request Body:**
```json
{
  "supplier_id": 1,
  "consumer_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": "10.00"
    },
    {
      "product_id": 2,
      "quantity": "5.00"
    }
  ],
  "delivery_method": "delivery",
  "delivery_address": "123 Main St, Almaty",
  "delivery_date": "2024-01-15T10:00:00Z",
  "notes": "Please deliver in the morning"
}
```

**Response:**
```json
{
  "id": 1,
  "order_number": "ORD-20240101120000-123456",
  "supplier_id": 1,
  "consumer_id": 1,
  "status": "pending",
  "subtotal": "50000.00",
  "total": "50000.00",
  "currency": "KZT",
  "delivery_method": "delivery",
  "delivery_address": "123 Main St, Almaty",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": "10.00",
      "unit_price": "5000.00",
      "total_price": "50000.00"
    }
  ],
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `201 CREATED`: Order created successfully
- `400 BAD REQUEST`: Invalid order data (insufficient stock, product unavailable, etc.)
- `403 FORBIDDEN`: Consumer must have accepted link with supplier
- `404 NOT FOUND`: Product not found
- `401 UNAUTHORIZED`: Not authenticated

---

#### GET `/orders/`
Get list of orders (filtered by user role).

**Headers:**
- `Authorization: Bearer <token>` (required)

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)
- `supplier_id`: Filter by supplier ID (integer, optional)
- `consumer_id`: Filter by consumer ID (integer, optional)
- `status`: Filter by status - `pending`, `accepted`, `rejected`, `in_progress`, `completed`, `cancelled` (string, optional)

**Response:**
```json
[
  {
    "id": 1,
    "order_number": "ORD-20240101120000-123456",
    "supplier_id": 1,
    "consumer_id": 1,
    "status": "pending",
    "total": "50000.00",
    "items": []
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `401 UNAUTHORIZED`: Not authenticated

---

#### GET `/orders/{order_id}`
Get order by ID.

**Headers:**
- `Authorization: Bearer <token>` (required)

**Path Parameters:**
- `order_id`: Order ID (integer, required)

**Response:**
```json
{
  "id": 1,
  "order_number": "ORD-20240101120000-123456",
  "supplier_id": 1,
  "consumer_id": 1,
  "status": "pending",
  "subtotal": "50000.00",
  "total": "50000.00",
  "currency": "KZT",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": "10.00",
      "unit_price": "5000.00",
      "total_price": "50000.00"
    }
  ],
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `403 FORBIDDEN`: Access denied (user doesn't have access to this order)
- `404 NOT FOUND`: Order not found
- `401 UNAUTHORIZED`: Not authenticated

---

#### PUT `/orders/{order_id}`
Update order status (accept/reject) - Supplier Owner/Manager only.

**Headers:**
- `Authorization: Bearer <token>` (required, Owner or Manager role)

**Path Parameters:**
- `order_id`: Order ID (integer, required)

**Request Body:**
```json
{
  "status": "accepted",
  "notes": "Order accepted, will be delivered tomorrow"
}
```

**Status Values:**
- `pending`: Initial status
- `accepted`: Order accepted by supplier
- `rejected`: Order rejected by supplier
- `in_progress`: Order being processed
- `completed`: Order completed
- `cancelled`: Order cancelled

**Response:**
```json
{
  "id": 1,
  "order_number": "ORD-20240101120000-123456",
  "status": "accepted",
  "accepted_at": "2024-01-01T13:00:00Z",
  "notes": "Order accepted, will be delivered tomorrow"
}
```

**Status Codes:**
- `200 OK`: Order updated successfully
- `403 FORBIDDEN`: Insufficient permissions (only owners and managers can accept/reject)
- `404 NOT FOUND`: Order not found
- `401 UNAUTHORIZED`: Not authenticated

---

## User Roles

### Consumer
- Can request links to suppliers
- Can view catalog and place orders once approved
- Can track orders
- Can log complaints tied to order details

### Owner
- Full control over supplier account
- Can create/remove Managers and Sales Representatives
- Can delete/deactivate supplier account
- All Manager capabilities

### Manager
- Handles catalog, inventory, and escalations
- Can manage orders (accept/reject)
- Can handle escalated complaints
- Cannot create/remove Managers or delete account

### Sales Representative
- Handles consumer communication
- Manages first-line complaints
- Escalates issues to Manager/Owner
- Can view orders and catalog

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Status Codes

- `200 OK`: Request successful
- `201 CREATED`: Resource created successfully
- `204 NO CONTENT`: Request successful, no content to return
- `400 BAD REQUEST`: Invalid request data
- `401 UNAUTHORIZED`: Authentication required or invalid token
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT FOUND`: Resource not found
- `422 UNPROCESSABLE ENTITY`: Validation error
- `500 INTERNAL SERVER ERROR`: Server error

---

## Rate Limiting

Rate limiting is not currently implemented but will be added in future versions.

---

## Pagination

List endpoints support pagination using `skip` and `limit` query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 1000)

---

## Date/Time Format

All date/time fields use ISO 8601 format:
```
2024-01-01T12:00:00Z
```

---

## Currency

All monetary values use Kazakhstani Tenge (KZT) as the default currency.

---

## Language Support

The API supports multiple languages:
- Kazakh (`kk`)
- Russian (`ru`)
- English (`en`) - default

Language can be specified in user profile and will be used for error messages and responses where applicable.

