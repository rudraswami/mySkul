"""
LLM Service - Unified interface for LLM API calls
Uses emergentintegrations library for consistent API access
Supports: OpenAI, DeepSeek, Qwen-VL
"""
import logging
import uuid
import asyncio
import os
from typing import Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

# Timeout constants
DEFAULT_LLM_TIMEOUT = 60.0  # 60 seconds (DeepSeek reasoning can take longer)
STREAMING_LLM_TIMEOUT = 180.0  # 3 minutes for streaming
DEEPSEEK_TIMEOUT = 90.0  # DeepSeek needs more time for deep reasoning

# Model configuration
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")


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


async def call_deepseek(
    prompt: str,
    api_key: str = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    model: str = None,
    session_id: Optional[str] = None,
    system_message: Optional[str] = None
) -> str:
    """
    Call DeepSeek API for deep reasoning tasks
    
    DeepSeek-R1 specializes in:
    - Complex multi-step reasoning
    - Mathematical proofs and derivations
    - Scientific explanations
    - Chain-of-thought problem solving
    
    Args:
        prompt: The prompt to send
        api_key: DeepSeek API key (falls back to env var)
        temperature: Creativity level (0.0-1.0)
        max_tokens: Maximum response length
        model: Model to use (default: deepseek-reasoner)
        session_id: Session ID for tracking
        system_message: System prompt
    
    Returns:
        DeepSeek response text
    """
    try:
        import litellm
        
        # Use provided key or fall back to env var
        actual_key = api_key or DEEPSEEK_API_KEY
        if not actual_key:
            logger.warning("⚠️ No DeepSeek API key - falling back to OpenAI (gpt-4.1-mini)")
            return await call_llm(prompt, os.environ.get('OPENAI_API_KEY', ''), 
                                  temperature, max_tokens, "gpt-4.1-mini", session_id, system_message)
        
        actual_model = model or DEEPSEEK_MODEL
        
        # Generate session ID if not provided
        if not session_id:
            session_id = f"deepseek_{str(uuid.uuid4())[:8]}"
        
        # Default system message for reasoning
        if not system_message:
            system_message = """You are DeepSeek, an advanced AI reasoning model specialized in:
- Multi-step mathematical and scientific reasoning
- Deep conceptual understanding
- Chain-of-thought problem solving
- Clear, structured explanations

Think step-by-step and show your reasoning process."""
        
        logger.info(f"🧠 Calling DeepSeek ({actual_model}) for deep reasoning...")
        
        # Use LiteLLM with DeepSeek configuration
        response = await asyncio.wait_for(
            litellm.acompletion(
                model=f"deepseek/{actual_model}",
                api_key=actual_key,
                api_base=DEEPSEEK_BASE_URL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            timeout=DEEPSEEK_TIMEOUT
        )
        
        result = response.choices[0].message.content
        logger.info(f"✅ DeepSeek response received ({len(result)} chars)")
        return result
        
    except asyncio.TimeoutError:
        logger.error(f"⏱️ DeepSeek call exceeded {DEEPSEEK_TIMEOUT}s timeout")
        raise Exception(f"DeepSeek timeout after {DEEPSEEK_TIMEOUT}s")
    except Exception as e:
        logger.error(f"❌ DeepSeek API call failed: {e}")
        # Fallback to standard LLM (gpt-4.1-mini)
        logger.info("↩️ Falling back to OpenAI gpt-4.1-mini...")
        return await call_llm(prompt, os.environ.get('OPENAI_API_KEY', ''),
                              temperature, max_tokens, "gpt-4.1-mini", session_id, system_message)


# =============================================================================
# GEMINI PRO - Primary reasoning model for AI Sathi
# =============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDsaHaCP3Xyctp7ndgwuX2NcY0wy8K-xUg")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro")
GEMINI_TIMEOUT = 45.0  # Gemini is fast, but allow time for complex reasoning


async def call_gemini(
    prompt: str,
    api_key: str = None,
    temperature: float = 0.7,
    max_tokens: int = 4000,
    model: str = None,
    session_id: Optional[str] = None,
    system_message: Optional[str] = None,
    use_pro: bool = False
) -> str:
    """
    Call Gemini API for intelligent reasoning tasks.
    
    Gemini Pro specializes in:
    - Lightning-fast responses
    - Deep conceptual understanding
    - Multi-modal reasoning (text + images)
    - Long context windows (1M+ tokens)
    - Educational content generation
    
    Args:
        prompt: The prompt to send
        api_key: Gemini API key (falls back to env var)
        temperature: Creativity level (0.0-1.0)
        max_tokens: Maximum response length
        model: Model to use (default: gemini-2.0-flash)
        session_id: Session ID for tracking
        system_message: System prompt
        use_pro: Use Gemini Pro for deeper reasoning (slower but more thorough)
    
    Returns:
        Gemini response text
    """
    try:
        import google.generativeai as genai
        
        # Use provided key or fall back to env var
        actual_key = api_key or GEMINI_API_KEY
        if not actual_key:
            logger.warning("⚠️ No Gemini API key - falling back to DeepSeek")
            return await call_deepseek(prompt, None, temperature, max_tokens, None, session_id, system_message)
        
        # Configure Gemini
        genai.configure(api_key=actual_key)
        
        # Select model
        actual_model = model or (GEMINI_PRO_MODEL if use_pro else GEMINI_MODEL)
        
        logger.info(f"⚡ Calling Gemini ({actual_model}) for intelligent response...")
        
        # Create the model
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=0.95,
            top_k=40
        )
        
        model_instance = genai.GenerativeModel(
            model_name=actual_model,
            generation_config=generation_config,
            system_instruction=system_message or _get_default_gemini_system_message()
        )
        
        # Generate response with timeout
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model_instance.generate_content(prompt)
            ),
            timeout=GEMINI_TIMEOUT
        )
        
        result = response.text
        logger.info(f"✅ Gemini response received ({len(result)} chars)")
        return result
        
    except asyncio.TimeoutError:
        logger.error(f"⏱️ Gemini call exceeded {GEMINI_TIMEOUT}s timeout")
        raise Exception(f"Gemini timeout after {GEMINI_TIMEOUT}s")
    except ImportError:
        logger.error("❌ google-generativeai not installed. Run: pip install google-generativeai")
        # Fallback to DeepSeek
        return await call_deepseek(prompt, None, temperature, max_tokens, None, session_id, system_message)
    except Exception as e:
        logger.error(f"❌ Gemini API call failed: {e}")
        # Fallback to DeepSeek
        logger.info("↩️ Falling back to DeepSeek...")
        return await call_deepseek(prompt, None, temperature, max_tokens, None, session_id, system_message)


def _get_default_gemini_system_message() -> str:
    """Default system message optimized for AI Sathi educational context"""
    return """You are AI Sathi, an elite AI tutor for Indian students preparing for JEE, NEET, and CBSE exams.

**CRITICAL: RESPONSE FORMATTING (ALWAYS FOLLOW)**

Every response MUST use proper markdown:

1. **HEADERS** - Use ## for main topics, ### for subtopics
2. **BOLD** - Use **bold** for key terms and definitions
3. **LISTS** - Use - bullets or 1. 2. 3. for numbered steps
4. **MATH** - Use \\( inline \\) and \\[ block \\] for LaTeX formulas
5. **CALLOUTS** - Use > for important notes/tips
6. **SPACING** - Separate sections with blank lines

**EXAMPLE FORMAT:**

## Topic Name

**Definition:** Clear definition here.

### Key Points
- Point 1 with explanation
- Point 2 with explanation

### Formula
\\[ F = ma \\]

> **Remember:** Key insight for exams.

**YOUR STYLE:**
- Friendly like a senior friend, BUT always structured
- Use relatable Indian examples (cricket, daily life)
- NEVER output unformatted paragraphs or walls of text
- Make responses scannable and easy to read

Remember: A student's career depends on understanding this correctly. Be accurate, be clear, be helpful, and WELL-FORMATTED."""


def get_reasoning_model_config() -> dict:
    """
    Get the best available reasoning model configuration.
    
    Priority:
    1. Gemini Pro (fastest, most intelligent)
    2. DeepSeek (deep reasoning fallback)
    3. GPT-4o (final fallback)
    
    Returns:
        dict with model, api_key, and provider info
    """
    from core.config import settings
    
    # Priority 1: Gemini Pro (primary)
    if getattr(settings, 'USE_GEMINI_PRIMARY', True) and getattr(settings, 'GEMINI_API_KEY', ''):
        return {
            "provider": "gemini",
            "model": settings.GEMINI_MODEL,
            "api_key": settings.GEMINI_API_KEY,
            "base_url": None,
            "call_function": call_gemini,
            "capabilities": ["fast", "conceptual", "visual", "long_context"]
        }
    
    # Priority 2: DeepSeek (deep reasoning)
    if settings.USE_DEEPSEEK_REASONING and settings.DEEPSEEK_API_KEY:
        return {
            "provider": "deepseek",
            "model": settings.DEEPSEEK_MODEL,
            "api_key": settings.DEEPSEEK_API_KEY,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "call_function": call_deepseek,
            "capabilities": ["deep_reasoning", "math", "proofs"]
        }
    
    # Priority 3: GPT-4.1-mini (primary base model)
    return {
        "provider": "openai",
        "model": settings.BASE_MODEL or "gpt-4.1-mini",
        "api_key": settings.OPENAI_API_KEY,
        "base_url": None,
        "call_function": call_llm,
        "capabilities": ["general", "creative", "math", "reasoning"]
    }


async def call_best_model(
    prompt: str,
    context: dict = None,
    temperature: float = 0.7,
    max_tokens: int = 4000,
    system_message: str = None
) -> str:
    """
    Automatically call the best available model based on configuration.
    
    Args:
        prompt: The prompt to send
        context: Optional context with query_type, complexity, etc.
        temperature: Creativity level
        max_tokens: Maximum response length
        system_message: System prompt
    
    Returns:
        Model response text
    """
    config = get_reasoning_model_config()
    call_fn = config["call_function"]
    
    logger.info(f"🧠 Using {config['provider']} ({config['model']}) for reasoning")
    
    return await call_fn(
        prompt=prompt,
        api_key=config["api_key"],
        temperature=temperature,
        max_tokens=max_tokens,
        system_message=system_message
    )

