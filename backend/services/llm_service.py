"""
LLM Service - Unified interface for LLM API calls
Uses emergentintegrations library for consistent API access
"""
import logging
import uuid
import asyncio
from typing import Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

# Timeout constants
DEFAULT_LLM_TIMEOUT = 30.0  # 30 seconds
STREAMING_LLM_TIMEOUT = 120.0  # 2 minutes for streaming


async def call_llm(
    prompt: str,
    api_key: str,
    temperature: float = 0.7,
    max_tokens: int = 500,
    model: str = "gpt-4o-mini",
    session_id: Optional[str] = None
) -> str:
    """
    Call LLM API with given prompt
    
    Args:
        prompt: The prompt to send to LLM
        api_key: API key for emergent integrations
        temperature: Creativity level (0.0-1.0) - NOTE: not used by LlmChat
        max_tokens: Maximum response length - NOTE: not used by LlmChat
        model: Model to use - NOTE: not used by LlmChat
        session_id: Session ID for LLM client (optional)
    
    Returns:
        LLM response text
    
    Raises:
        Exception: If LLM call fails
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = f"llm_{str(uuid.uuid4())[:8]}"
        
        # Initialize LLM client with correct API
        # NOTE: LlmChat from emergentintegrations uses api_key + session_id
        # temperature/max_tokens/model are not supported in constructor
        llm_client = LlmChat(
            api_key=api_key,
            session_id=session_id
        )
        
        # Create user message
        user_msg = UserMessage(content=prompt)
        
        # Get response with timeout protection
        try:
            response = await asyncio.wait_for(
                llm_client.send_message_async(user_msg),
                timeout=DEFAULT_LLM_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"⏱️ LLM call exceeded {DEFAULT_LLM_TIMEOUT}s timeout")
            raise Exception(f"LLM call timeout after {DEFAULT_LLM_TIMEOUT}s")
        
        if not response or not response.content:
            raise Exception("Empty response from LLM")
        
        return response.content
        
    except Exception as e:
        logger.error(f"❌ LLM API call failed: {e}")
        raise Exception(f"LLM call failed: {str(e)}")


async def call_llm_streaming(
    prompt: str,
    api_key: str,
    temperature: float = 0.7,
    max_tokens: int = 500,
    model: str = "gpt-4o-mini",
    session_id: Optional[str] = None
):
    """
    Call LLM API with streaming response
    
    Args:
        prompt: The prompt to send to LLM
        api_key: API key for emergent integrations
        temperature: Creativity level (0.0-1.0) - NOTE: not used by LlmChat
        max_tokens: Maximum response length - NOTE: not used by LlmChat
        model: Model to use - NOTE: not used by LlmChat
        session_id: Session ID for LLM client (optional)
    
    Yields:
        Response chunks as they arrive
    
    Raises:
        Exception: If LLM call fails
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = f"llm_stream_{str(uuid.uuid4())[:8]}"
        
        # Initialize LLM client with correct API
        llm_client = LlmChat(
            api_key=api_key,
            session_id=session_id
        )
        
        # Create user message
        user_msg = UserMessage(content=prompt)
        
        # NOTE: Check if stream_message_async exists, otherwise use send_message_async
        if hasattr(llm_client, 'stream_message_async'):
            # Stream response
            async for chunk in llm_client.stream_message_async(user_msg):
                if chunk and hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
        else:
            # Fallback to non-streaming
            response = await llm_client.send_message_async(user_msg)
            if response and response.content:
                yield response.content
        
    except Exception as e:
        logger.error(f"❌ LLM streaming call failed: {e}")
        raise Exception(f"LLM streaming failed: {str(e)}")

