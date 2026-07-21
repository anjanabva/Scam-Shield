import logging
from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator
from openai import AsyncOpenAI
import config

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("openai_client")

# Global tracker for token budget
token_usage_tracker = {
    "total_prompt_tokens": 0,
    "total_completion_tokens": 0,
    "total_tokens": 0
}

# Initialize Async client
# We use AsyncOpenAI for compatibility with FastAPI
try:
    client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

async def get_llm_response(
    messages: List[Dict[str, str]], 
    model: str = config.LLM_MODEL,
    temperature: float = 0.0,
    response_format: Optional[Dict[str, str]] = None
) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Sends a request to the LLM and tracks token usage.
    
    Args:
        messages: List of message dicts (role, content).
        model: The model to use (default from config).
        temperature: Temperature for generation.
        response_format: Optional JSON format parameter.
        
    Returns:
        A tuple of (content_string, usage_dict).
    """
    if not client:
        logger.error("OpenAI client is not initialized. Check API key.")
        return None, {}

    try:
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = await client.chat.completions.create(**kwargs)
        
        # Extract response
        content = response.choices[0].message.content
        
        # Track usage
        usage = response.usage
        if usage:
            usage_data = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }
            
            # Update global tracker
            token_usage_tracker["total_prompt_tokens"] += usage.prompt_tokens
            token_usage_tracker["total_completion_tokens"] += usage.completion_tokens
            token_usage_tracker["total_tokens"] += usage.total_tokens
            
            logger.info(f"LLM Call Usage: {usage_data}")
            logger.info(f"Session Total Tokens: {token_usage_tracker['total_tokens']}")
            
            return content, usage_data
            
        return content, {}
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return None, {}

async def stream_llm_response(
    messages: List[Dict[str, str]], 
    model: str = config.LLM_MODEL,
    temperature: float = 0.7
) -> AsyncGenerator[str, None]:
    """
    Streams a response from the LLM.
    """
    if not client:
        logger.error("OpenAI client is not initialized.")
        yield "Error: AI engine is unreachable."
        return

    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True
        )
        
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content
                
    except Exception as e:
        logger.error(f"Error streaming from OpenAI: {e}")
        yield "\n\n[Error: Connection lost]"

async def get_embedding(text: str, model: str = config.EMBEDDING_MODEL) -> List[float]:
    """
    Generates an embedding for the given text.
    """
    if not client:
        logger.error("OpenAI client is not initialized.")
        return []
        
    try:
        response = await client.embeddings.create(
            input=[text],
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return []