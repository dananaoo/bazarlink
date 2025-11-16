# Authentication Guide for FastAPI Docs

## How to Authorize in Swagger UI

When you click the **"Authorize"** button in FastAPI docs, you'll see an OAuth2 modal. Here's what to fill in:

### Required Fields (for Password Flow)

1. **username**: Enter your email address
   - Example: `admin@test.com`
   - ⚠️ Note: OAuth2 uses "username" field, but enter your **email** here

2. **password**: Enter your password
   - Example: `admin123`

### Optional Fields (can be left empty)

3. **client_id**: Leave empty (not required for password flow)
4. **client_secret**: Leave empty (not required for password flow)

### Steps to Authorize

1. **First, get a token** by using the login endpoint:
   - Go to `POST /api/v1/auth/login`
   - Click "Try it out"
   - Enter:
     - `username`: `admin@test.com`
     - `password`: `admin123`
   - Click "Execute"
   - Copy the `access_token` from the response

2. **Then authorize**:
   - Click the "Authorize" button (top right, lock icon 🔒)
   - In the modal, you have two options:

   **Option A: Use the form (for getting token)**
   - Fill in `username` and `password`
   - Click "Authorize"
   - This will automatically get a token for you

   **Option B: Paste token directly (recommended)**
   - After getting token from login endpoint
   - In the authorization modal, find the field for the token
   - Paste: `Bearer <your_access_token>`
   - Or just paste the token (FastAPI adds "Bearer" automatically)
   - Click "Authorize"

3. **Close the modal** and test endpoints!

## Quick Test Credentials

- **Email/Username**: `admin@test.com`
- **Password**: `admin123`

## Alternative: Direct Token Entry

If the OAuth2 form is confusing, you can:

1. Use `POST /api/v1/auth/login` to get token
2. Copy the `access_token` value
3. Click "Authorize"
4. Look for a field that says "Value" or "Bearer token"
5. Paste your token there
6. Click "Authorize"

The token format should be: `Bearer <long_jwt_token_string>`

## Troubleshooting

**"Invalid credentials" error?**
- Make sure you're using email as username
- Check password is correct
- Verify user exists: `docker exec scp_postgres psql -U postgres -d scp_db -c "SELECT email FROM users;"`

**Token not working?**
- Make sure you copied the entire token (it's a long string)
- Include "Bearer " prefix if the field requires it
- Check token hasn't expired (default: 30 minutes)

**Can't see "Authorize" button?**
- Make sure you're on `/docs` page (not `/redoc`)
- Refresh the page
- Check browser console for errors

