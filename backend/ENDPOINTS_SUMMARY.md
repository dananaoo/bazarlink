# API Endpoints Summary

This document summarizes all API endpoints and their role-based access controls according to the business requirements.

## Authentication Endpoints

### `POST /api/v1/auth/login`
- **Public**: Yes
- **Description**: User login for all roles
- **Request**: `username` (email), `password`
- **Response**: JWT token

### `GET /api/v1/auth/me`
- **Public**: No (requires authentication)
- **Description**: Get current user information
- **Roles**: All

### `POST /api/v1/auth/register-owner`
- **Public**: Yes
- **Description**: Register a new owner with supplier (web app registration)
- **Request**: Owner details + Supplier details
- **Response**: Created user

---

## User Management Endpoints

### `POST /api/v1/users/`
- **Public**: No
- **Description**: Create a new user (Owner only)
- **Roles**: OWNER
- **Restrictions**: Owner can only create MANAGER and SALES_REPRESENTATIVE users
- **Request**: User details (role must be MANAGER or SALES_REPRESENTATIVE)

### `GET /api/v1/users/`
- **Public**: No
- **Description**: List users
- **Roles**: All authenticated users

### `GET /api/v1/users/{user_id}`
- **Public**: No
- **Description**: Get user by ID
- **Roles**: All authenticated users

### `PUT /api/v1/users/{user_id}`
- **Public**: No
- **Description**: Update user
- **Roles**: All authenticated users

---

## Supplier Endpoints

### `POST /api/v1/suppliers/`
- **Public**: No
- **Description**: Create a new supplier
- **Roles**: OWNER
- **Note**: Usually created during owner registration via `/api/v1/auth/register-owner`, but owners can create additional suppliers if needed

### `GET /api/v1/suppliers/`
- **Public**: No
- **Description**: List suppliers
- **Roles**: All authenticated users

### `GET /api/v1/suppliers/{supplier_id}`
- **Public**: No
- **Description**: Get supplier by ID
- **Roles**: All authenticated users

### `PUT /api/v1/suppliers/{supplier_id}`
- **Public**: No
- **Description**: Update supplier (including description)
- **Roles**: OWNER, MANAGER
- **Note**: Owner can edit supplier description and all other fields

---

## Consumer Endpoints

### `POST /api/v1/consumers/`
- **Public**: Yes
- **Description**: Create a new consumer

### `GET /api/v1/consumers/`
- **Public**: No
- **Description**: List consumers
- **Roles**: All authenticated users

### `GET /api/v1/consumers/{consumer_id}`
- **Public**: No
- **Description**: Get consumer by ID
- **Roles**: All authenticated users

### `PUT /api/v1/consumers/{consumer_id}`
- **Public**: No
- **Description**: Update consumer
- **Roles**: All authenticated users

---

## Link Endpoints (Supplier-Consumer Relationships)

### `POST /api/v1/links/`
- **Public**: No
- **Description**: Request a link to a supplier (Consumer) or invite a consumer (Supplier)
- **Roles**: CONSUMER, OWNER, MANAGER, SALES_REPRESENTATIVE
- **Note**: Consumers request links via mobile app

### `GET /api/v1/links/`
- **Public**: No
- **Description**: List links
- **Roles**: All authenticated users
- **Filters**: `supplier_id`, `consumer_id`, `status`

### `GET /api/v1/links/{link_id}`
- **Public**: No
- **Description**: Get link by ID
- **Roles**: All authenticated users

### `PUT /api/v1/links/{link_id}`
- **Public**: No
- **Description**: Approve/reject link request
- **Roles**: OWNER, MANAGER, SALES_REPRESENTATIVE (web app)
- **Note**: Sales reps can approve/reject links in web app

---

## Product Endpoints

### `POST /api/v1/products/`
- **Public**: No
- **Description**: Create a new product
- **Roles**: OWNER, MANAGER

### `GET /api/v1/products/`
- **Public**: No
- **Description**: List products
- **Roles**: All authenticated users
- **Restrictions**: 
  - **CONSUMER**: Can only see products from suppliers they have ACCEPTED links with
  - **OWNER/MANAGER/SALES_REPRESENTATIVE**: See all products for their supplier
- **Filters**: `supplier_id`

### `GET /api/v1/products/{product_id}`
- **Public**: No
- **Description**: Get product by ID
- **Roles**: All authenticated users
- **Restrictions**: Same as list endpoint

### `PUT /api/v1/products/{product_id}`
- **Public**: No
- **Description**: Update product
- **Roles**: OWNER, MANAGER

### `DELETE /api/v1/products/{product_id}`
- **Public**: No
- **Description**: Delete product
- **Roles**: OWNER, MANAGER

---

## Order Endpoints

### `POST /api/v1/orders/`
- **Public**: No
- **Description**: Create a new order
- **Roles**: CONSUMER (mobile app)
- **Restrictions**: Consumer must have ACCEPTED link with supplier

### `GET /api/v1/orders/`
- **Public**: No
- **Description**: List orders
- **Roles**: All authenticated users
- **Restrictions**: 
  - **CONSUMER**: See only their orders
  - **OWNER/MANAGER/SALES_REPRESENTATIVE**: See orders for their supplier
- **Filters**: `supplier_id`, `consumer_id`, `status`

### `GET /api/v1/orders/{order_id}`
- **Public**: No
- **Description**: Get order by ID
- **Roles**: All authenticated users
- **Restrictions**: Same as list endpoint

### `PUT /api/v1/orders/{order_id}`
- **Public**: No
- **Description**: Update order (accept/reject)
- **Roles**: OWNER, MANAGER (web app)

---

## Message Endpoints (Chat)

### `POST /api/v1/messages/`
- **Public**: No
- **Description**: Send a message
- **Roles**: CONSUMER (mobile app), SALES_REPRESENTATIVE (mobile app + web app)
- **Restrictions**: Link must be ACCEPTED
- **Note**: Consumers and sales reps can chat in mobile app

### `GET /api/v1/messages/`
- **Public**: No
- **Description**: Get messages for a link
- **Roles**: CONSUMER, SALES_REPRESENTATIVE, MANAGER, OWNER
- **Parameters**: `link_id` (required)
- **Note**: Messages are automatically marked as read when fetched

### `PUT /api/v1/messages/{message_id}/read`
- **Public**: No
- **Description**: Mark message as read
- **Roles**: All authenticated users

---

## Complaint Endpoints

### `POST /api/v1/complaints/`
- **Public**: No
- **Description**: Create a complaint
- **Roles**: CONSUMER (mobile app)
- **Restrictions**: Can only create complaints for own orders

### `GET /api/v1/complaints/`
- **Public**: No
- **Description**: List complaints
- **Roles**: All authenticated users
- **Restrictions**:
  - **CONSUMER**: See only their complaints
  - **SALES_REPRESENTATIVE**: See complaints at SALES level for their supplier
  - **MANAGER**: See escalated complaints (MANAGER level) for their supplier
  - **OWNER**: See all complaints EXCEPT escalated ones (no escalated problems)
- **Filters**: `supplier_id`, `consumer_id`, `status`, `level`

### `GET /api/v1/complaints/{complaint_id}`
- **Public**: No
- **Description**: Get complaint by ID
- **Roles**: All authenticated users
- **Restrictions**: Same as list endpoint

### `POST /api/v1/complaints/{complaint_id}/escalate`
- **Public**: No
- **Description**: Escalate complaint to manager
- **Roles**: SALES_REPRESENTATIVE (mobile app + web app)
- **Request**: `escalated_to_user_id` (must be a manager)

### `PUT /api/v1/complaints/{complaint_id}`
- **Public**: No
- **Description**: Update complaint (resolve, change status)
- **Roles**: SALES_REPRESENTATIVE, MANAGER
- **Restrictions**:
  - **SALES_REPRESENTATIVE**: Can only update complaints at SALES level
  - **MANAGER**: Can only update escalated complaints (MANAGER level)

---

## Incident Endpoints (Escalated Problems)

### `POST /api/v1/incidents/`
- **Public**: No
- **Description**: Create an incident
- **Roles**: MANAGER (web app)

### `GET /api/v1/incidents/`
- **Public**: No
- **Description**: List incidents (escalated problems)
- **Roles**: MANAGER (web app)
- **Restrictions**: Only managers can see escalated problems
- **Note**: Owners CANNOT see escalated incidents
- **Filters**: `supplier_id`, `status`, `assigned_to_user_id`

### `GET /api/v1/incidents/{incident_id}`
- **Public**: No
- **Description**: Get incident by ID
- **Roles**: MANAGER (web app)

### `PUT /api/v1/incidents/{incident_id}`
- **Public**: No
- **Description**: Update incident (resolve, assign, change status)
- **Roles**: MANAGER (web app)
- **Note**: Managers can answer, resolve, and give status updates

---

## Role-Based Access Summary

### CONSUMER (Mobile App)
- ✅ Login
- ✅ Request links to suppliers
- ✅ View products from approved suppliers only
- ✅ Create orders (for approved suppliers)
- ✅ Chat with sales representatives
- ✅ Create complaints
- ✅ View own complaints

### SALES_REPRESENTATIVE (Mobile App + Web App)
- ✅ Login
- ✅ Approve/reject link requests (web app)
- ✅ Chat with consumers (mobile app + web app)
- ✅ View and update complaints at SALES level
- ✅ Escalate complaints to managers
- ❌ Cannot see escalated problems (incidents)

### MANAGER (Web App)
- ✅ Login
- ✅ Approve/reject link requests
- ✅ Create/edit products
- ✅ Accept/reject orders
- ✅ View escalated problems (incidents)
- ✅ Resolve incidents
- ✅ Update incident status
- ✅ Answer escalated complaints
- ✅ Chat with consumers (via messages)

### OWNER (Web App)
- ✅ Register (public endpoint)
- ✅ Login
- ✅ Create managers and sales representatives
- ✅ Edit supplier description and all supplier fields
- ✅ Approve/reject link requests
- ✅ Create/edit products
- ✅ Accept/reject orders
- ✅ View all complaints (except escalated)
- ✅ Chat with consumers (via messages)
- ✅ All abilities of managers and sales reps
- ❌ Cannot see escalated problems (incidents)

---

## Important Notes

1. **Link Approval Flow**: 
   - Consumer requests link → Sales Rep/Manager/Owner approves → Consumer can see catalog

2. **Product Visibility**: 
   - Consumers only see products after link is ACCEPTED

3. **Escalation Flow**:
   - Consumer creates complaint → Sales Rep handles → Sales Rep escalates to Manager → Manager resolves
   - Owners cannot see escalated problems (incidents)

4. **Chat Flow**:
   - Consumer and Sales Rep can chat in mobile app
   - Sales Rep can also chat in web app
   - Messages are linked to accepted links

5. **User Creation**:
   - Owners can only create Managers and Sales Representatives
   - All created users are automatically associated with owner's supplier

