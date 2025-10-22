# ==================== config/bible_config.py ====================

import os
from dotenv import load_dotenv

load_dotenv()


class BibleConfig:
    """Configuration for Bible API."""
    
    # Bible API settings
    BASE_URL = "https://bible-api.com"
    
    # Default translation (KJV, ASV, WEB, etc.)
    DEFAULT_TRANSLATION = os.getenv("BIBLE_TRANSLATION", "KJV")
    
    # Timeout for API requests (seconds)
    TIMEOUT = int(os.getenv("BIBLE_API_TIMEOUT", "10"))
    
    # Maximum retries for failed requests
    MAX_RETRIES = int(os.getenv("BIBLE_API_MAX_RETRIES", "3"))
    
    # Cache settings
    ENABLE_CACHE = os.getenv("BIBLE_ENABLE_CACHE", "True").lower() == "true"
    CACHE_TTL_HOURS = int(os.getenv("BIBLE_CACHE_TTL_HOURS", "168"))  # 7 days
    
    @classmethod
    def get_verse_url(cls, reference: str) -> str:
        """
        Generate Bible API URL for a verse reference.
        
        Args:
            reference: Bible reference (e.g., "John 3:16", "Matthew 7:7")
            
        Returns:
            Full API URL
        """
        # Clean reference: replace spaces with +
        clean_ref = reference.strip().replace(" ", "+")
        return f"{cls.BASE_URL}/{clean_ref}?translation={cls.DEFAULT_TRANSLATION}"


