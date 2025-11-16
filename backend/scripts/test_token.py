"""
Test script to decode and verify JWT tokens
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.core.security import decode_access_token
from jose import jwt
from datetime import datetime

# Token from the user's request
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjIsInJvbGUiOiJvd25lciIsImV4cCI6MTc2MzMwMjQwNH0.yZD9a9J2p8UQbDHFFHzAdWWF2CFZ_5rNtxFQKbF_zho"

print("=" * 60)
print("Token Debugging")
print("=" * 60)
print(f"SECRET_KEY: {settings.SECRET_KEY}")
print(f"ALGORITHM: {settings.ALGORITHM}")
print()

# Try to decode without verification first (to see payload)
try:
    # Decode without verification
    from jose import jwt as jose_jwt
    unverified = jose_jwt.decode(token, key="dummy", options={"verify_signature": False, "verify_exp": False})
    print("Token payload (unverified):")
    print(f"  sub (user_id): {unverified.get('sub')}")
    print(f"  role: {unverified.get('role')}")
    exp = unverified.get('exp')
    if exp:
        exp_time = datetime.fromtimestamp(exp)
        now = datetime.utcnow()
        print(f"  exp: {exp_time} (UTC)")
        print(f"  now: {now} (UTC)")
        print(f"  expired: {exp_time < now}")
        if exp_time < now:
            print("  WARNING: TOKEN HAS EXPIRED!")
    print()
except Exception as e:
    print(f"Error decoding token (unverified): {e}")
    import traceback
    traceback.print_exc()
    print()

# Try to decode with verification
print("Attempting to decode with verification...")
payload = decode_access_token(token)
if payload:
    print("SUCCESS: Token decoded successfully!")
    print(f"  Payload: {payload}")
else:
    print("FAILED: Token decode failed!")
    print("  Possible reasons:")
    print("    1. SECRET_KEY mismatch")
    print("    2. Token signature invalid")
    print("    3. Token expired")
    print()
    
    # Try with different common secret keys
    test_keys = [
        "your-secret-key-change-in-production",
        "your-secret-key-change-in-production-use-strong-random-key",
    ]
    
    print("Testing with different SECRET_KEY values...")
    for test_key in test_keys:
        try:
            test_payload = jwt.decode(token, test_key, algorithms=["HS256"])
            print(f"  SUCCESS: Works with: {test_key}")
            print(f"     Payload: {test_payload}")
            print()
            print("SOLUTION: Update your .env file or config to use this SECRET_KEY!")
            break
        except Exception as e:
            print(f"  FAILED with: {test_key}")

print()
print("=" * 60)

