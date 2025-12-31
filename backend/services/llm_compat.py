"""
Compatibility wrapper to replace emergentintegrations.LlmChat
Uses OpenAI SDK directly while maintaining the same interface
"""
from openai import AsyncOpenAI
from typing import Optional


class LlmChat:
    """
    Compatibility wrapper for emergentintegrations.LlmChat
    Uses OpenAI SDK directly
    """
    def __init__(self, api_key: str, session_id: Optional[str] = None, system_message: Optional[str] = None):
        self.api_key = api_key
        self.session_id = session_id
        self.system_message = system_message or "You are a helpful AI assistant."
        self.client = AsyncOpenAI(api_key=api_key)
        self._model = "gpt-4o-mini"
        self._params = {}
    
    def with_model(self, provider: str, model: str):
        """Set the model (provider is ignored, we use OpenAI)"""
        self._model = model
        return self
    
    def with_params(self, **kwargs):
        """Set parameters"""
        self._params.update(kwargs)
        return self
    
    async def send_message(self, message):
        """Send message and get response"""
        import asyncio
        
        # Extract text from UserMessage if it's an object, otherwise use string directly
        if hasattr(message, 'text'):
            user_content = message.text
        elif isinstance(message, str):
            user_content = message
        else:
            user_content = str(message)
        
        response = await self.client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_content}
            ],
            **self._params
        )
        
        if not response or not response.choices:
            raise Exception("Empty response from LLM")
        
        result = response.choices[0].message.content
        return result if result else ""
    
    async def stream_message(self, message):
        """Stream message response"""
        # Extract text from UserMessage if it's an object, otherwise use string directly
        if hasattr(message, 'text'):
            user_content = message.text
        elif isinstance(message, str):
            user_content = message
        else:
            user_content = str(message)
        
        stream = await self.client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": user_content}
            ],
            stream=True,
            **self._params
        )
        
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class UserMessage:
    """Compatibility wrapper for emergentintegrations.UserMessage"""
    def __init__(self, text: str):
        self.text = text

