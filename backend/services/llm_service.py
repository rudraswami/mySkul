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
    session_id: Optional[str] = None,
    system_message: Optional[str] = None
) -> str:
    """
    Call LLM API with given prompt
    
    Args:
        prompt: The prompt to send to LLM
        api_key: API key for emergent integrations
        temperature: Creativity level (0.0-1.0)
        max_tokens: Maximum response length
        model: Model to use (e.g., "gpt-4o-mini")
        session_id: Session ID for LLM client (optional)
        system_message: System message for LLM context (optional)
    
    Returns:
        LLM response text
    
    Raises:
        Exception: If LLM call fails
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = f"llm_{str(uuid.uuid4())[:8]}"
        
        # Default system message if not provided
        if not system_message:
            system_message = "You are a helpful AI assistant. Respond concisely and accurately."
        
        # Initialize LLM client with correct API
        llm_client = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", model).with_params(
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Create user message
        user_msg = UserMessage(text=prompt)
        
        # Get response with timeout protection
        try:
            response = await asyncio.wait_for(
                llm_client.send_message(user_msg),
                timeout=DEFAULT_LLM_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"⏱️ LLM call exceeded {DEFAULT_LLM_TIMEOUT}s timeout")
            raise Exception(f"LLM call timeout after {DEFAULT_LLM_TIMEOUT}s")
        
        if not response:
            raise Exception("Empty response from LLM")
        
        # Response is already a string (or needs to be converted)
        return response if isinstance(response, str) else str(response)
        
    except Exception as e:
        logger.error(f"❌ LLM API call failed: {e}")
        raise Exception(f"LLM call failed: {str(e)}")


async def call_llm_streaming(
    prompt: str,
    api_key: str,
    temperature: float = 0.7,
    max_tokens: int = 500,
    model: str = "gpt-4o-mini",
    session_id: Optional[str] = None,
    system_message: Optional[str] = None
):
    """
    Call LLM API with streaming response
    
    Args:
        prompt: The prompt to send to LLM
        api_key: API key for emergent integrations
        temperature: Creativity level (0.0-1.0)
        max_tokens: Maximum response length
        model: Model to use (e.g., "gpt-4o-mini")
        session_id: Session ID for LLM client (optional)
        system_message: System message for LLM context (optional)
    
    Yields:
        Response chunks as they arrive
    
    Raises:
        Exception: If LLM call fails
    """
    try:
        # Generate session ID if not provided
        if not session_id:
            session_id = f"llm_stream_{str(uuid.uuid4())[:8]}"
        
        # Default system message if not provided
        if not system_message:
            system_message = "You are a helpful AI assistant. Respond concisely and accurately."
        
        # Initialize LLM client with correct API
        llm_client = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", model).with_params(
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Create user message
        user_msg = UserMessage(text=prompt)
        
        # NOTE: Check if stream_message exists, otherwise use send_message
        if hasattr(llm_client, 'stream_message'):
            # Stream response
            async for chunk in llm_client.stream_message(user_msg):
                if chunk:
                    # Handle both string and object responses
                    if isinstance(chunk, str):
                        yield chunk
                    elif hasattr(chunk, 'content') and chunk.content:
                        yield chunk.content
        else:
            # Fallback to non-streaming
            response = await llm_client.send_message(user_msg)
            if response:
                # Response is already a string or needs conversion
                yield response if isinstance(response, str) else str(response)
        
    except Exception as e:
        logger.error(f"❌ LLM streaming call failed: {e}")
        raise Exception(f"LLM streaming failed: {str(e)}")

