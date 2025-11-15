# Testing Guide

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
# or just test dependencies:
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=app --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

### Run Specific Test File

```bash
pytest tests/test_auth.py
```

### Run Specific Test

```bash
pytest tests/test_auth.py::test_login_success
```

### Run Tests with Verbose Output

```bash
pytest -v
```

## Test Structure

```
tests/
├── conftest.py          # Pytest fixtures and configuration
├── test_auth.py         # Authentication endpoint tests
├── test_users.py        # User endpoint tests
├── test_suppliers.py    # Supplier endpoint tests
├── test_consumers.py    # Consumer endpoint tests
├── test_products.py     # Product endpoint tests
├── test_links.py        # Link endpoint tests
└── test_orders.py      # Order endpoint tests
```

## Test Database

Tests use an in-memory SQLite database that is created fresh for each test. This ensures:
- Tests are isolated from each other
- No need for a running PostgreSQL instance
- Fast test execution
- Clean database state for each test

## Fixtures

### Database Fixtures
- `db_session`: Provides a fresh database session for each test

### Client Fixtures
- `client`: Provides a FastAPI test client with database override

### User Fixtures
- `test_supplier`: Creates a test supplier
- `test_consumer`: Creates a test consumer
- `test_owner_user`: Creates a test owner user
- `test_consumer_user`: Creates a test consumer user

### Authentication Fixtures
- `auth_headers_owner`: Provides authentication headers for owner user
- `auth_headers_consumer`: Provides authentication headers for consumer user

## Writing New Tests

### Example Test Structure

```python
def test_endpoint_name(client, auth_headers_owner):
    """Test description"""
    # Arrange
    data = {
        "field": "value"
    }
    
    # Act
    response = client.post(
        "/api/v1/endpoint/",
        json=data,
        headers=auth_headers_owner
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["field"] == "value"
```

## Test Coverage

Current test coverage includes:
- ✅ Authentication endpoints
- ✅ User management endpoints
- ✅ Supplier CRUD operations
- ✅ Consumer CRUD operations
- ✅ Product management
- ✅ Link requests and approval
- ✅ Order creation and management

## Continuous Integration

Tests should be run in CI/CD pipeline before deployment. Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest
```

