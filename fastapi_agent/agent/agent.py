"""
LangChain agent setup with Google Gemini.
Creates and configures the agent for BGV workflows using LangChain 1.1.0+ API.
"""
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.tools import ALL_TOOLS
from agent.prompts import AGENT_SYSTEM_PROMPT
from core.config import settings
from core.rate_limiter import get_rate_limiter
import logging
import time

logger = logging.getLogger(__name__)


def create_bgv_agent():
    logger.info(f"Initializing BGV agent with model: {settings.gemini_model}")

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.1,
        # Add retry configuration for quota errors
        max_retries=3,
    )

    agent = create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=AGENT_SYSTEM_PROMPT,
        debug=True  
    )

    logger.info("BGV agent initialized successfully")
    return agent


_agent = None
_cached_model = None


def get_agent():
    """
    Get or create the agent instance.
    Automatically recreates agent if model has changed.
    """
    global _agent, _cached_model
    
    current_model = settings.gemini_model
    
    # Recreate agent if model changed or agent doesn't exist
    if _agent is None or _cached_model != current_model:
        logger.info(f"Creating new agent instance (model: {current_model})")
        _agent = create_bgv_agent()
        _cached_model = current_model
    else:
        logger.debug(f"Using cached agent instance (model: {current_model})")
    
    return _agent


def reset_agent():
    """Force reset of cached agent (useful for testing or model changes)."""
    global _agent, _cached_model
    _agent = None
    _cached_model = None
    logger.info("Agent cache reset")


def invoke_agent_with_rate_limit(agent, messages, max_retries=3):
    """
    Invoke agent with rate limiting and quota error handling.
    
    Args:
        agent: The agent instance
        messages: Messages to send to agent
        max_retries: Maximum retry attempts for quota errors
        
    Returns:
        Agent result
        
    Raises:
        Exception: If all retries exhausted or non-quota error occurs
    """
    rate_limiter = get_rate_limiter()
    
    for attempt in range(max_retries + 1):
        try:
            # Acquire rate limit token
            if not rate_limiter.acquire(wait=True):
                raise Exception("Rate limiter failed to acquire token")
            
            # Invoke agent
            result = agent.invoke({"messages": messages})
            return result
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if it's a quota/rate limit error
            is_quota_error = any(keyword in error_str for keyword in [
                'quota',
                'rate limit',
                'resourceexhausted',
                '429',
                'exceeded'
            ])
            
            if is_quota_error and attempt < max_retries:
                # Exponential backoff for quota errors
                wait_time = (2 ** attempt) * 10  # 10s, 20s, 40s
                logger.warning(
                    f"Quota error detected (attempt {attempt + 1}/{max_retries + 1}). "
                    f"Waiting {wait_time}s before retry..."
                )
                time.sleep(wait_time)
                continue
            else:
                # Non-quota error or max retries reached
                logger.error(f"Agent invocation failed: {str(e)}")
                raise
