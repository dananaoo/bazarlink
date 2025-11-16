# Token Authentication Fix

## Problem
Getting 401 "Could not validate credentials" when using tokens in FastAPI docs.

## Root Causes
1. **SECRET_KEY mismatch**: Token was created with one SECRET_KEY but server is using a different one
2. **User ID format**: JWT library expects `sub` claim to be a string, but we were storing integer

## Solution Applied

### 1. Fixed User ID Storage
- Changed token creation to store user ID as string: `str(user.id)`
- Updated token decoding to handle both string and integer user IDs

### 2. SECRET_KEY Consistency
- Docker backend uses: `your-secret-key-change-in-production`
- Make sure your `.env` file (if running locally) uses the same key

## How to Fix Your Current Issue

**You need to get a NEW token** because:
1. The code changed (user_id is now stored as string)
2. Your old token might have been created with a different SECRET_KEY

### Steps:
1. **Get a new token**:
   - Go to `POST /api/v1/auth/login` in FastAPI docs
   - Enter:
     - `username`: `admin@test.com`
     - `password`: `admin123`
   - Click "Execute"
   - Copy the NEW `access_token`

2. **Authorize with the new token**:
   - Click "Authorize" button
   - Paste the new token (or use the form with username/password)
   - Click "Authorize"

3. **Test `/api/v1/auth/me`** - it should work now!

## Verify SECRET_KEY

If you're still having issues, check the SECRET_KEY:

**In Docker**:
```bash
docker exec scp_backend python -c "from app.core.config import settings; print(settings.SECRET_KEY)"
```

**Locally** (if running backend locally):
```bash
cd backend
python -c "from app.core.config import settings; print(settings.SECRET_KEY)"
```

Both should match: `your-secret-key-change-in-production`

## Note
The backend auto-reloads when code changes. If you're still seeing the old error, wait a few seconds for the reload, then try getting a new token.

