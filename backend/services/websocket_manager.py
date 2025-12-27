"""
🔌 WebSocket Manager - Real-Time Notification Delivery
=======================================================

This module provides real-time WebSocket connectivity for instant
notification delivery. Falls back gracefully to polling if WebSocket
is unavailable.

Features:
- Connection management per user
- Automatic reconnection handling
- Graceful degradation (polling fallback)
- Thread-safe connection registry
- Heartbeat/ping-pong for connection health

Integration:
- Injected into NotificationService
- Used by /ws/notifications endpoint
- Non-blocking: if WebSocket fails, notification still stored
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Set, Optional, Any
from dataclasses import dataclass, field
from weakref import WeakSet
from fastapi import WebSocket, WebSocketDisconnect
import uuid

logger = logging.getLogger(__name__)


@dataclass
class UserConnection:
    """Represents a WebSocket connection for a user"""
    user_id: str
    websocket: WebSocket
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_ping: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'connection_id': self.connection_id,
            'connected_at': self.connected_at.isoformat(),
            'last_ping': self.last_ping.isoformat()
        }


class WebSocketManager:
    """
    Manages WebSocket connections for real-time notification delivery.
    
    Thread-safe and designed for production use:
    - Multiple connections per user (different devices)
    - Automatic cleanup of dead connections
    - Graceful error handling
    """
    
    def __init__(self):
        # user_id -> Set of UserConnection
        self._connections: Dict[str, Set[UserConnection]] = {}
        self._lock = asyncio.Lock()
        self._heartbeat_interval = 30  # seconds
        self._connection_timeout = 120  # seconds without ping = dead
        
        logger.info("🔌 WebSocketManager initialized")
    
    async def connect(self, websocket: WebSocket, user_id: str) -> UserConnection:
        """
        Register a new WebSocket connection for a user.
        
        Args:
            websocket: The WebSocket connection
            user_id: The authenticated user ID
            
        Returns:
            UserConnection object
        """
        await websocket.accept()
        
        connection = UserConnection(
            user_id=user_id,
            websocket=websocket
        )
        
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = set()
            self._connections[user_id].add(connection)
        
        logger.info(f"🔌 WebSocket connected: user={user_id}, conn={connection.connection_id}")
        
        # Send welcome message
        try:
            await websocket.send_json({
                'type': 'connected',
                'connection_id': connection.connection_id,
                'message': 'Real-time notifications enabled'
            })
        except Exception as e:
            logger.warning(f"Failed to send welcome message: {e}")
        
        return connection
    
    async def disconnect(self, user_id: str, connection: UserConnection):
        """
        Remove a WebSocket connection.
        
        Args:
            user_id: The user ID
            connection: The connection to remove
        """
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].discard(connection)
                if not self._connections[user_id]:
                    del self._connections[user_id]
        
        logger.info(f"🔌 WebSocket disconnected: user={user_id}, conn={connection.connection_id}")
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to all connections for a user.
        
        This is the main method used by NotificationService.
        
        Args:
            user_id: Target user
            message: Message to send (will be JSON-serialized)
            
        Returns:
            Delivery status with success/failure counts
        """
        async with self._lock:
            connections = self._connections.get(user_id, set()).copy()
        
        if not connections:
            return {
                'delivered': False,
                'reason': 'no_active_connections',
                'connection_count': 0
            }
        
        success_count = 0
        failed_connections = []
        
        for conn in connections:
            try:
                await conn.websocket.send_json(message)
                success_count += 1
                conn.last_ping = datetime.now(timezone.utc)
            except Exception as e:
                logger.warning(f"Failed to send to {conn.connection_id}: {e}")
                failed_connections.append(conn)
        
        # Clean up failed connections
        if failed_connections:
            async with self._lock:
                for conn in failed_connections:
                    if user_id in self._connections:
                        self._connections[user_id].discard(conn)
        
        if success_count > 0:
            logger.debug(f"📤 WebSocket delivery: user={user_id}, sent={success_count}, failed={len(failed_connections)}")
            return {
                'delivered': True,
                'success_count': success_count,
                'failed_count': len(failed_connections),
                'connection_count': len(connections)
            }
        else:
            return {
                'delivered': False,
                'reason': 'all_connections_failed',
                'failed_count': len(failed_connections)
            }
    
    async def broadcast(self, message: Dict[str, Any], user_ids: Optional[list] = None):
        """
        Broadcast a message to multiple users (or all connected users).
        
        Args:
            message: Message to broadcast
            user_ids: Optional list of user IDs (None = all users)
        """
        async with self._lock:
            targets = user_ids or list(self._connections.keys())
        
        results = {}
        for user_id in targets:
            result = await self.send_to_user(user_id, message)
            results[user_id] = result
        
        return results
    
    def get_connected_users(self) -> list:
        """Get list of currently connected user IDs"""
        return list(self._connections.keys())
    
    def get_connection_count(self, user_id: str = None) -> int:
        """Get connection count (for a user or total)"""
        if user_id:
            return len(self._connections.get(user_id, set()))
        return sum(len(conns) for conns in self._connections.values())
    
    def is_user_connected(self, user_id: str) -> bool:
        """Check if a user has any active WebSocket connections"""
        return user_id in self._connections and len(self._connections[user_id]) > 0
    
    async def handle_client_message(self, user_id: str, connection: UserConnection, data: str):
        """
        Handle incoming message from client.
        
        Supports:
        - ping: Heartbeat response
        - ack: Notification acknowledgment
        """
        try:
            message = json.loads(data)
            msg_type = message.get('type', '')
            
            if msg_type == 'ping':
                connection.last_ping = datetime.now(timezone.utc)
                await connection.websocket.send_json({'type': 'pong'})
            
            elif msg_type == 'ack':
                # Client acknowledged receiving a notification
                notification_id = message.get('notification_id')
                logger.debug(f"📬 Notification ack: {notification_id} from {user_id}")
            
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from client: {data[:100]}")
        except Exception as e:
            logger.warning(f"Error handling client message: {e}")
    
    async def cleanup_stale_connections(self):
        """
        Remove connections that haven't responded to heartbeat.
        Run this periodically (e.g., every 60 seconds).
        """
        now = datetime.now(timezone.utc)
        timeout_threshold = now.timestamp() - self._connection_timeout
        
        stale = []
        
        async with self._lock:
            for user_id, connections in list(self._connections.items()):
                for conn in list(connections):
                    if conn.last_ping.timestamp() < timeout_threshold:
                        stale.append((user_id, conn))
        
        for user_id, conn in stale:
            try:
                await conn.websocket.close(code=1000, reason="Connection timeout")
            except:
                pass
            await self.disconnect(user_id, conn)
        
        if stale:
            logger.info(f"🧹 Cleaned up {len(stale)} stale WebSocket connections")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        return {
            'total_users': len(self._connections),
            'total_connections': self.get_connection_count(),
            'users': {
                user_id: len(conns) 
                for user_id, conns in self._connections.items()
            }
        }


# Global WebSocket manager instance
_ws_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Get or create the global WebSocket manager"""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager


def init_websocket_manager() -> WebSocketManager:
    """Initialize the global WebSocket manager (call at startup)"""
    global _ws_manager
    _ws_manager = WebSocketManager()
    return _ws_manager

