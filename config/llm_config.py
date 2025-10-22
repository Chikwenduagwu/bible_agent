

import os
from dotenv import load_dotenv

load_dotenv()


class LLMConfig:
    """Configuration for FireworksAI LLM."""
    
    
    API_KEY = os.getenv("FIREWORKS_API_KEY", "")
    BASE_URL = "https://api.fireworks.ai/inference/v1"
    
   
    MODEL = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/llama-v3p1-8b-instruct")
    
    
    MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))
    TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
    
    
    TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))
    
    # System prompt for Bible verse explanations
    SYSTEM_PROMPT = """You are a knowledgeable Bible scholar and teacher. 
Your role is to explain Bible verses in a clear, accurate, and accessible way.

When explaining verses:
1. Provide historical and cultural context
2. Explain the meaning in simple terms
3. Highlight key theological concepts
4. Relate it to the broader biblical narrative
5. Make it relevant to modern readers

Be respectful, accurate, and educational in your explanations."""
    
    @classmethod
    def validate(cls) -> bool:
        """Validate LLM configuration."""
        if not cls.API_KEY:
            print("❌ FIREWORKS_API_KEY is not set")
            return False
        return True

