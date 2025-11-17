# Chat Testing Guide

This guide shows you how to test the chat functionality without a frontend.

## Prerequisites

1. **Backend must be running** on `http://localhost:8000`
2. **Database must have:**
   - At least one supplier (owner)
   - At least one consumer
   - A link between them with status `accepted`
   - Sales representatives (optional, for testing assignment)

## Method 1: Python Test Script (Recommended)

### Setup

Install required Python packages:
```bash
cd backend
pip install websockets requests
```

### Run the Test Script

```bash
python test_chat.py
```

The script will:
1. Ask for your email and password
2. Login and get a JWT token
3. Show available links (chats)
4. Let you select a link
5. Connect to WebSocket chat
6. Allow you to send/receive messages interactively

**Example usage:**
```
Email: consumer@test.com
Password: password123

[Select link]
1. Link ID: 1 (Supplier: 1, Consumer: 1)
Select link (1-1): 1

[WEBSOCKET] Ready! Type messages (or 'quit' to exit):
[Consumer] > Hello!
[WEBSOCKET] ✓ Message sent! ID: 42
```

## Method 2: Using curl for REST API

### Step 1: Login and Get Token

```bash
# Login as consumer
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=consumer@test.com&password=password123" \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

### Step 2: Get Links (Chats)

```bash
curl -X GET "http://localhost:8000/api/v1/links/?consumer_id=1" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

### Step 3: Get Messages

```bash
curl -X GET "http://localhost:8000/api/v1/messages/?link_id=1" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

### Step 4: Create Message (REST)

```bash
curl -X POST "http://localhost:8000/api/v1/messages/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "link_id": 1,
    "content": "Hello from curl!",
    "message_type": "text"
  }' | jq '.'
```

### Step 5: Assign Chat (Sales Rep only)

```bash
curl -X POST "http://localhost:8000/api/v1/links/1/assign" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

## Method 3: Using websocat (Command Line)

### Install websocat

**macOS:**
```bash
brew install websocat
```

**Linux:**
```bash
# Download from https://github.com/vi/websocat/releases
# Or use cargo: cargo install websocat
```

### Connect to WebSocket

```bash
# First, get your token (see Method 2, Step 1)
TOKEN="your_jwt_token_here"

# Connect to WebSocket
websocat "ws://localhost:8000/api/v1/ws/chat/1?token=$TOKEN"
```

### Send Messages

Once connected, you can type JSON messages:

```json
{"type": "message", "content": "Hello from websocat!", "message_type": "text"}
```

```json
{"type": "typing", "is_typing": true, "link_id": 1}
```

```json
{"type": "ping"}
```

## Method 4: Using wscat (Node.js)

### Install wscat

```bash
npm install -g wscat
```

### Connect to WebSocket

```bash
# Get token first (see Method 2, Step 1)
TOKEN="your_jwt_token_here"

# Connect
wscat -c "ws://localhost:8000/api/v1/ws/chat/1?token=$TOKEN"
```

### Send Messages

Once connected, type JSON messages:
```json
{"type": "message", "content": "Hello!", "message_type": "text"}
```

## Method 5: Browser Console (Quick Test)

Open browser console (F12) and run:

```javascript
// 1. Get token first (use curl or login via API)
const token = "your_jwt_token_here";
const linkId = 1;

// 2. Connect to WebSocket
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/chat/${linkId}?token=${token}`);

// 3. Handle messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Received:", data);
};

// 4. Send message
ws.onopen = () => {
    console.log("Connected!");
    ws.send(JSON.stringify({
        type: "message",
        content: "Hello from browser!",
        message_type: "text"
    }));
};

// 5. Send typing indicator
ws.send(JSON.stringify({
    type: "typing",
    is_typing: true,
    link_id: linkId
}));
```

## Method 6: Using Postman

Postman supports WebSocket connections (newer versions).

1. **Create WebSocket Request:**
   - New → WebSocket Request
   - URL: `ws://localhost:8000/api/v1/ws/chat/1?token=YOUR_TOKEN`

2. **Connect:**
   - Click "Connect"
   - You should see connection confirmation

3. **Send Messages:**
   - In the message box, type JSON:
   ```json
   {"type": "message", "content": "Hello!", "message_type": "text"}
   ```

## Testing Scenarios

### Scenario 1: Consumer sends message to Supplier

1. Login as consumer → Get token
2. Connect to WebSocket with consumer token
3. Send message
4. Supplier (or sales rep) should receive it

### Scenario 2: Sales Rep responds

1. Login as sales rep → Get token
2. Assign chat: `POST /api/v1/links/{link_id}/assign`
3. Connect to WebSocket with sales rep token
4. Send message
5. Consumer should receive it

### Scenario 3: Multiple Sales Reps

1. Sales Rep 1 assigns chat to themselves
2. Sales Rep 2 connects to same chat (should work - no restriction)
3. Both can send messages
4. Messages will have `sales_rep_id` set to the sender

### Scenario 4: Get "My Chats" vs "Other Chats"

**As Sales Rep:**

```bash
# My chats (assigned to me)
curl -X GET "http://localhost:8000/api/v1/links/chats/my" \
  -H "Authorization: Bearer $SALES_REP_TOKEN" | jq '.'

# Other chats (unassigned or assigned to others)
curl -X GET "http://localhost:8000/api/v1/links/chats/other" \
  -H "Authorization: Bearer $SALES_REP_TOKEN" | jq '.'
```

## Troubleshooting

### "Connection failed: 1008"
- Token is invalid or expired
- User doesn't have access to this link
- Link status is not `accepted`

### "No links found"
- Create a link first: `POST /api/v1/links/`
- Accept the link: `PUT /api/v1/links/{link_id}` with `{"status": "accepted"}`

### "WebSocket connection refused"
- Backend is not running
- Wrong port (should be 8000)
- WebSocket endpoint not registered (check `app/api/v1/api.py`)

### Messages not appearing
- Check if link status is `accepted`
- Verify user has access to the link
- Check backend logs for errors

## Quick Test Checklist

- [ ] Backend running on port 8000
- [ ] Database has at least one accepted link
- [ ] User accounts exist (consumer, sales rep, etc.)
- [ ] Can login and get token
- [ ] Can get links
- [ ] Can connect to WebSocket
- [ ] Can send messages
- [ ] Can receive messages
- [ ] Messages saved to database
- [ ] Sales rep assignment works
- [ ] "My chats" vs "Other chats" works

## Example Test Flow

```bash
# Terminal 1: Consumer
python test_chat.py
# Login as consumer@test.com
# Select link 1
# Type: "Hello supplier!"

# Terminal 2: Sales Rep
python test_chat.py
# Login as salesrep@test.com
# Select link 1
# See consumer's message
# Type: "Hi consumer! How can I help?"
```

Both terminals should see each other's messages in real-time!

