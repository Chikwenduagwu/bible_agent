"""
FireworksAI LLM Service for explaining Bible verses.
Place this in: src/bible_agent/llm_service.py
"""

import aiohttp
import logging
from typing import AsyncIterator, Dict
from config.llm_config import LLMConfig

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with FireworksAI Llama model."""
    
    def __init__(self):
        self.config = LLMConfig()
        
        if not self.config.validate():
            raise ValueError("Invalid LLM configuration")
        
        self.headers = {
            "Authorization": f"Bearer {self.config.API_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"🤖 LLM initialized: {self.config.MODEL}")
    
    async def explain_verse(
        self, 
        verse_reference: str, 
        verse_text: str,
        user_question: str = None
    ) -> AsyncIterator[str]:
        """
        Get explanation for a Bible verse using streaming.
        
        Args:
            verse_reference: The verse reference (e.g., "Matthew 7:7")
            verse_text: The actual verse text
            user_question: Optional specific question about the verse
            
        Yields:
            Chunks of the explanation text
        """
        
        # Build the prompt
        if user_question:
            prompt = f"""The user asks: "{user_question}"

Here is the relevant Bible verse:

**{verse_reference}**
{verse_text}

Please provide a comprehensive explanation that addresses the user's question."""
        else:
            prompt = f"""Please explain this Bible verse:

**{verse_reference}**
{verse_text}

Provide context, meaning, and practical application."""
        
        # Prepare the API request
        payload = {
            "model": self.config.MODEL,
            "messages": [
                {"role": "system", "content": self.config.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.MAX_TOKENS,
            "temperature": self.config.TEMPERATURE,
            "top_p": self.config.TOP_P,
            "stream": True
        }
        
        url = f"{self.config.BASE_URL}/chat/completions"
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    url, 
                    json=payload, 
                    headers=self.headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"❌ LLM API error: {response.status} - {error_text}")
                        yield f"Error: Unable to generate explanation (Status: {response.status})"
                        return
                    
                    # Stream the response
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        
                        if not line or line == "data: [DONE]":
                            continue
                        
                        if line.startswith("data: "):
                            try:
                                import json
                                json_str = line[6:]  # Remove "data: " prefix
                                data = json.loads(json_str)
                                
                                # Extract the content delta
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        yield content
                                        
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                logger.error(f"Error parsing stream: {str(e)}")
                                continue
                    
        except aiohttp.ClientError as e:
            logger.error(f"❌ Network error: {str(e)}")
            yield f"Error: Network error occurred - {str(e)}"
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            yield f"Error: An unexpected error occurred - {str(e)}"
    
    async def explain_verse_complete(
        self, 
        verse_reference: str, 
        verse_text: str,
        user_question: str = None
    ) -> str:
        """
        Get complete explanation (non-streaming version).
        
        Args:
            verse_reference: The verse reference
            verse_text: The actual verse text
            user_question: Optional specific question
            
        Returns:
            Complete explanation text
        """
        
        # Build the prompt
        if user_question:
            prompt = f"""The user asks: "{user_question}"

Here is the relevant Bible verse:

**{verse_reference}**
{verse_text}

Please provide a comprehensive explanation that addresses the user's question."""
        else:
            prompt = f"""Please explain this Bible verse:

**{verse_reference}**
{verse_text}

Provide context, meaning, and practical application."""
        
        # Prepare the API request (no streaming)
        payload = {
            "model": self.config.MODEL,
            "messages": [
                {"role": "system", "content": self.config.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.MAX_TOKENS,
            "temperature": self.config.TEMPERATURE,
            "top_p": self.config.TOP_P,
            "stream": False
        }
        
        url = f"{self.config.BASE_URL}/chat/completions"
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    url, 
                    json=payload, 
                    headers=self.headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"❌ LLM API error: {response.status}")
                        return f"Error: Unable to generate explanation"
                    
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    return content
                    
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return f"Error: {str(e)}"