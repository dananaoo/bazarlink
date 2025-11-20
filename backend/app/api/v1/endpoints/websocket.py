"""
WebSocket endpoints for real-time chat
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Set
import json
import logging
from app.core.dependencies import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.models.message import Message
from app.models.link import Link, LinkStatus
from app.models.consumer import Consumer

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active WebSocket connections: {user_id: {link_id: websocket}}
active_connections: Dict[int, Dict[int, WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, link_id: int):
        """Connect a user to a chat room (link)"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        
        self.active_connections[user_id][link_id] = websocket
        logger.info(f"User {user_id} connected to chat {link_id}")
    
    def disconnect(self, user_id: int, link_id: int):
        """Disconnect a user from a chat room"""
        if user_id in self.active_connections:
            if link_id in self.active_connections[user_id]:
                del self.active_connections[user_id][link_id]
                logger.info(f"User {user_id} disconnected from chat {link_id}")
            
            # Clean up empty user entries
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int, link_id: int):
        """Send message to a specific user in a specific chat"""
        if user_id in self.active_connections and link_id in self.active_connections[user_id]:
            websocket = self.active_connections[user_id][link_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id, link_id)
    
    async def broadcast_to_chat(self, message: dict, link_id: int, exclude_user_id: int = None):
        """Broadcast message to all users in a chat room"""
        # Find all users connected to this chat
        for user_id, links in self.active_connections.items():
            if link_id in links and user_id != exclude_user_id:
                await self.send_personal_message(message, user_id, link_id)


manager = ConnectionManager()


async def get_user_from_token(token: str, db: Session) -> User:
    """Authenticate user from WebSocket token"""
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.websocket("/chat/{link_id}")
async def websocket_chat(
    websocket: WebSocket,
    link_id: int
):
    """
    WebSocket endpoint for real-time chat
    
    Query parameters (in URL):
    - token: JWT access token for authentication
    Example: ws://host/api/v1/ws/chat/1?token=your_jwt_token
    
    The WebSocket connection allows real-time messaging in a chat (link).
    Messages are broadcast to all connected users in the same chat.
    """
    from app.db.session import SessionLocal
    
    user = None
    db = SessionLocal()
    
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token required")
            return
        
        # Authenticate user
        user = await get_user_from_token(token, db)
        
        # Verify link exists
        link = db.query(Link).filter(Link.id == link_id).first()
        if not link:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Verify user has access to this link
        if user.role == UserRole.CONSUMER:
            if link.consumer_id != user.consumer_id:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        elif user.role in [UserRole.SALES_REPRESENTATIVE, UserRole.MANAGER, UserRole.OWNER]:
            if link.supplier_id != user.supplier_id:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        else:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Verify link is accepted
        if link.status != LinkStatus.ACCEPTED:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Connect to chat room
        await manager.connect(websocket, user.id, link_id)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "link_id": link_id,
            "user_id": user.id
        })
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "message":
                # Create new message
                content = data.get("content") or ""
                attachment_url = data.get("attachment_url")
                
                # Validate that either content or attachment_url is provided
                if not content and not attachment_url:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Either content or attachment_url must be provided"
                    })
                    continue
                
                # Determine message type
                if attachment_url:
                    msg_type = "attachment"
                else:
                    msg_type = data.get("message_type", "text")
                
                # Determine receiver
                receiver_id = None
                sales_rep_id = None
                
                if user.role == UserRole.CONSUMER:
                    # Consumer messages go to supplier (receiver_id can be None)
                    receiver_id = data.get("receiver_id")  # Optional: specific sales rep
                elif user.role in [UserRole.SALES_REPRESENTATIVE, UserRole.MANAGER, UserRole.OWNER]:
                    # Supplier staff messages go to consumer
                    consumer = db.query(Consumer).filter(Consumer.id == link.consumer_id).first()
                    receiver_id = consumer.user.id if consumer and consumer.user else None
                    # Only set sales_rep_id for sales representatives, not for managers/owners
                    if user.role == UserRole.SALES_REPRESENTATIVE:
                        sales_rep_id = user.id
                
                # Create message in database
                db_message = Message(
                    link_id=link_id,
                    sender_id=user.id,
                    receiver_id=receiver_id,
                    sales_rep_id=sales_rep_id,
                    content=content,
                    message_type=msg_type,
                    attachment_url=attachment_url,
                    attachment_type=data.get("attachment_type"),
                    product_id=data.get("product_id"),
                    order_id=data.get("order_id")
                )
                db.add(db_message)
                db.commit()
                db.refresh(db_message)
                
                # Prepare message for broadcast
                message_data = {
                    "type": "new_message",
                    "message": {
                        "id": db_message.id,
                        "link_id": db_message.link_id,
                        "sender_id": db_message.sender_id,
                        "receiver_id": db_message.receiver_id,
                        "sales_rep_id": db_message.sales_rep_id,
                        "content": db_message.content,
                        "message_type": db_message.message_type,
                        "attachment_url": db_message.attachment_url,
                        "attachment_type": db_message.attachment_type,
                        "product_id": db_message.product_id,
                        "order_id": db_message.order_id,
                        "is_read": db_message.is_read,
                        "created_at": db_message.created_at.isoformat()
                    }
                }
                
                # Broadcast to all users in this chat (except sender)
                await manager.broadcast_to_chat(message_data, link_id, exclude_user_id=user.id)
                
                # Send confirmation to sender
                await websocket.send_json({
                    "type": "message_sent",
                    "message_id": db_message.id
                })
            
            elif message_type == "typing":
                # Broadcast typing indicator
                typing_data = {
                    "type": "typing",
                    "user_id": user.id,
                    "link_id": link_id,
                    "is_typing": data.get("is_typing", True)
                }
                await manager.broadcast_to_chat(typing_data, link_id, exclude_user_id=user.id)
            
            elif message_type == "ping":
                # Keep-alive ping
                await websocket.send_json({"type": "pong"})
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        if user:
            manager.disconnect(user.id, link_id)
        logger.info(f"User {user.id if user else 'Unknown'} disconnected from chat {link_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if user:
            manager.disconnect(user.id, link_id)
        try:
            await websocket.close()
        except:
            pass
    finally:
        db.close()

