"""
🔌 WebSocket API - Real-Time Notification Endpoint
===================================================

This module provides the WebSocket endpoint for real-time notifications.

Endpoint: ws://host/ws/notifications
Authentication: Token in query parameter (ws://...?token=xyz)

Usage:
1. Client connects with auth token
2. Server sends notifications in real-time
3. Client can send ping/ack messages
4. Falls back to polling if WebSocket unavailable
"""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import Optional
import jwt
import os

from services.websocket_manager import get_websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


async def authenticate_websocket(token: str) -> Optional[str]:
    """
    Authenticate WebSocket connection via JWT token.
    
    Returns user_id if valid, None otherwise.
    """
    if not token:
        return None
    
    try:
        # Try JWT token
        secret_key = os.environ.get('JWT_SECRET_KEY', os.environ.get('SECRET_KEY', 'dev-secret'))
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload.get('sub') or payload.get('user_id')
    except jwt.ExpiredSignatureError:
        logger.warning("WebSocket auth: Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"WebSocket auth: Invalid token - {e}")
        return None
    except Exception as e:
        logger.warning(f"WebSocket auth failed: {e}")
        return None


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(None)
):
    """
    WebSocket endpoint for real-time notifications.
    
    Connect with: ws://host/ws/notifications?token=<jwt_token>
    
    Messages from server:
    - {"type": "connected", "connection_id": "...", "message": "..."}
    - {"type": "notification", "notification": {...}}
    - {"type": "pong"}
    
    Messages from client:
    - {"type": "ping"}
    - {"type": "ack", "notification_id": "..."}
    """
    # Authenticate
    user_id = await authenticate_websocket(token)
    
    if not user_id:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    # Get WebSocket manager
    ws_manager = get_websocket_manager()
    
    # Connect
    connection = await ws_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            await ws_manager.handle_client_message(user_id, connection, data)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {user_id}")
    except Exception as e:
        logger.warning(f"WebSocket error for {user_id}: {e}")
    finally:
        await ws_manager.disconnect(user_id, connection)


@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection statistics.
    
    Useful for monitoring and debugging.
    """
    ws_manager = get_websocket_manager()
    stats = ws_manager.get_stats()
    
    return {
        "websocket_enabled": True,
        "stats": stats
    }


@router.get("/ws/user/{user_id}/connected")
async def check_user_connected(user_id: str):
    """
    Check if a specific user has active WebSocket connections.
    """
    ws_manager = get_websocket_manager()
    
    return {
        "user_id": user_id,
        "connected": ws_manager.is_user_connected(user_id),
        "connection_count": ws_manager.get_connection_count(user_id)
    }

