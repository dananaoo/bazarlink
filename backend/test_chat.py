#!/usr/bin/env python3
"""
Test script for WebSocket chat functionality
Usage: python test_chat.py
"""
import asyncio
import json
import sys
from typing import Optional

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
except ImportError:
    print("ERROR: websockets library not installed")
    print("Install it with: pip install websockets")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed")
    print("Install it with: pip install requests")
    sys.exit(1)


# Configuration
API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"


def login(email: str, password: str) -> Optional[str]:
    """Login and get JWT token"""
    url = f"{API_BASE_URL}/api/v1/auth/login"
    data = {
        "username": email,  # OAuth2 uses 'username' field for email
        "password": password
    }
    
    print(f"\n[LOGIN] Logging in as {email}...")
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"[LOGIN] ✓ Success! Token: {token[:50]}...")
        return token
    else:
        print(f"[LOGIN] ✗ Failed: {response.status_code} - {response.text}")
        return None


def get_user_info(token: str):
    """Get current user information"""
    url = f"{API_BASE_URL}/api/v1/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user = response.json()
        print(f"[USER INFO] ID: {user['id']}, Role: {user['role']}, Email: {user['email']}")
        return user
    else:
        print(f"[USER INFO] ✗ Failed: {response.status_code}")
        return None


def get_links(token: str, supplier_id: int = None, consumer_id: int = None):
    """Get links (chats)"""
    url = f"{API_BASE_URL}/api/v1/links/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if supplier_id:
        params["supplier_id"] = supplier_id
    if consumer_id:
        params["consumer_id"] = consumer_id
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        links = response.json()
        print(f"\n[LINKS] Found {len(links)} link(s):")
        for link in links:
            print(f"  - Link ID: {link['id']}, Status: {link['status']}, "
                  f"Supplier: {link['supplier_id']}, Consumer: {link['consumer_id']}, "
                  f"Assigned to: {link.get('assigned_sales_rep_id', 'None')}")
        return links
    else:
        print(f"[LINKS] ✗ Failed: {response.status_code} - {response.text}")
        return []


def assign_chat(token: str, link_id: int):
    """Assign chat to current sales rep"""
    url = f"{API_BASE_URL}/api/v1/links/{link_id}/assign"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n[ASSIGN] Assigning chat {link_id}...")
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        link = response.json()
        print(f"[ASSIGN] ✓ Success! Chat assigned to sales rep {link.get('assigned_sales_rep_id')}")
        return link
    else:
        print(f"[ASSIGN] ✗ Failed: {response.status_code} - {response.text}")
        return None


def get_messages(token: str, link_id: int):
    """Get messages for a link"""
    url = f"{API_BASE_URL}/api/v1/messages/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"link_id": link_id}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        messages = response.json()
        print(f"\n[MESSAGES] Found {len(messages)} message(s) for link {link_id}:")
        for msg in messages:
            sender = f"User {msg['sender_id']}"
            if msg.get('sales_rep_id'):
                sender += f" (Sales Rep {msg['sales_rep_id']})"
            print(f"  - [{msg['created_at']}] {sender}: {msg['content']}")
        return messages
    else:
        print(f"[MESSAGES] ✗ Failed: {response.status_code} - {response.text}")
        return []


def create_message(token: str, link_id: int, content: str):
    """Create a message via REST API"""
    url = f"{API_BASE_URL}/api/v1/messages/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "link_id": link_id,
        "content": content,
        "message_type": "text"
    }
    
    print(f"\n[CREATE MESSAGE] Sending message via REST...")
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        message = response.json()
        print(f"[CREATE MESSAGE] ✓ Success! Message ID: {message['id']}")
        return message
    else:
        print(f"[CREATE MESSAGE] ✗ Failed: {response.status_code} - {response.text}")
        return None


async def websocket_chat(token: str, link_id: int, user_name: str = "User"):
    """Connect to WebSocket chat and send/receive messages"""
    ws_url = f"{WS_BASE_URL}/api/v1/ws/chat/{link_id}?token={token}"
    
    print(f"\n[WEBSOCKET] Connecting to chat {link_id}...")
    print(f"[WEBSOCKET] URL: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"[WEBSOCKET] ✓ Connected!")
            
            # Wait for connection confirmation
            try:
                confirmation = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                conf_data = json.loads(confirmation)
                print(f"[WEBSOCKET] Connection confirmed: {conf_data}")
            except asyncio.TimeoutError:
                print("[WEBSOCKET] No confirmation received (continuing anyway)")
            
            # Start receiving messages in background
            async def receive_messages():
                try:
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        msg_type = data.get("type")
                        
                        if msg_type == "new_message":
                            msg = data.get("message", {})
                            sender = f"User {msg.get('sender_id')}"
                            if msg.get('sales_rep_id'):
                                sender += f" (Sales Rep {msg.get('sales_rep_id')})"
                            print(f"\n[WEBSOCKET] 📨 NEW MESSAGE from {sender}:")
                            print(f"    Content: {msg.get('content')}")
                            print(f"    Time: {msg.get('created_at')}")
                        elif msg_type == "typing":
                            print(f"\n[WEBSOCKET] ⌨️  User {data.get('user_id')} is typing...")
                        elif msg_type == "message_sent":
                            print(f"[WEBSOCKET] ✓ Message sent! ID: {data.get('message_id')}")
                        elif msg_type == "pong":
                            print(f"[WEBSOCKET] Pong received")
                        elif msg_type == "error":
                            print(f"[WEBSOCKET] ✗ Error: {data.get('message')}")
                        else:
                            print(f"[WEBSOCKET] Received: {data}")
                except websockets.exceptions.ConnectionClosed:
                    print(f"\n[WEBSOCKET] Connection closed")
                except Exception as e:
                    print(f"\n[WEBSOCKET] Error receiving: {e}")
            
            # Start receiver task
            receive_task = asyncio.create_task(receive_messages())
            
            # Interactive message sending
            print(f"\n[WEBSOCKET] Ready! Type messages (or 'quit' to exit):")
            print("  Commands:")
            print("    - Type any message to send it")
            print("    - 'quit' or 'exit' to disconnect")
            print("    - 'typing' to send typing indicator")
            print("    - 'ping' to send keep-alive")
            
            try:
                while True:
                    # Read from stdin (non-blocking)
                    message = await asyncio.get_event_loop().run_in_executor(
                        None, input, f"\n[{user_name}] > "
                    )
                    
                    if message.lower() in ['quit', 'exit', 'q']:
                        print("[WEBSOCKET] Disconnecting...")
                        break
                    
                    if message.lower() == 'typing':
                        await websocket.send(json.dumps({
                            "type": "typing",
                            "is_typing": True,
                            "link_id": link_id
                        }))
                        print("[WEBSOCKET] Sent typing indicator")
                        continue
                    
                    if message.lower() == 'ping':
                        await websocket.send(json.dumps({"type": "ping"}))
                        print("[WEBSOCKET] Sent ping")
                        continue
                    
                    # Send message
                    message_data = {
                        "type": "message",
                        "content": message,
                        "message_type": "text"
                    }
                    await websocket.send(json.dumps(message_data))
                    print(f"[WEBSOCKET] Sent message: {message}")
            
            except KeyboardInterrupt:
                print("\n[WEBSOCKET] Interrupted by user")
            finally:
                receive_task.cancel()
                try:
                    await receive_task
                except asyncio.CancelledError:
                    pass
    
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"[WEBSOCKET] ✗ Connection failed: {e.status_code}")
        if e.status_code == 1008:
            print("[WEBSOCKET] Authentication failed or access denied")
    except Exception as e:
        print(f"[WEBSOCKET] ✗ Error: {e}")


async def main():
    """Main test function"""
    print("=" * 60)
    print("CHAT TESTING SCRIPT")
    print("=" * 60)
    
    # Get credentials
    print("\nEnter credentials:")
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    # Login
    token = login(email, password)
    if not token:
        print("\n✗ Login failed. Exiting.")
        return
    
    # Get user info
    user = get_user_info(token)
    if not user:
        print("\n✗ Failed to get user info. Exiting.")
        return
    
    # Get links
    links = get_links(token)
    if not links:
        print("\n⚠ No links found. You need to create a link first.")
        print("  1. Create a link between supplier and consumer")
        print("  2. Accept the link (status must be 'accepted')")
        print("  3. Then run this script again")
        return
    
    # Filter accepted links
    accepted_links = [link for link in links if link['status'] == 'accepted']
    if not accepted_links:
        print("\n⚠ No accepted links found. Please accept a link first.")
        return
    
    print(f"\n[SELECT LINK] Found {len(accepted_links)} accepted link(s)")
    for i, link in enumerate(accepted_links, 1):
        print(f"  {i}. Link ID: {link['id']} (Supplier: {link['supplier_id']}, Consumer: {link['consumer_id']})")
    
    link_choice = input(f"\nSelect link (1-{len(accepted_links)}): ").strip()
    try:
        link_idx = int(link_choice) - 1
        selected_link = accepted_links[link_idx]
        link_id = selected_link['id']
    except (ValueError, IndexError):
        print("✗ Invalid selection")
        return
    
    # If sales rep, offer to assign chat
    if user['role'] == 'sales_representative':
        assign = input("\nAssign this chat to yourself? (y/n): ").strip().lower()
        if assign == 'y':
            assign_chat(token, link_id)
    
    # Show existing messages
    get_messages(token, link_id)
    
    # Connect to WebSocket
    user_name = user.get('full_name') or user.get('email', 'User')
    await websocket_chat(token, link_id, user_name)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

