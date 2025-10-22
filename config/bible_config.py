
import os
from dotenv import load_dotenv

load_dotenv()


class BibleConfig:
    """Configuration for Bible API."""
    
    
    BASE_URL = "https://bible-api.com"
    
    
    DEFAULT_TRANSLATION = os.getenv("BIBLE_TRANSLATION", "KJV")
    
   
    TIMEOUT = int(os.getenv("BIBLE_API_TIMEOUT", "10"))
    
   
    MAX_RETRIES = int(os.getenv("BIBLE_API_MAX_RETRIES", "3"))
    
    
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
      
        clean_ref = reference.strip().replace(" ", "+")
        return f"{cls.BASE_URL}/{clean_ref}?translation={cls.DEFAULT_TRANSLATION}"



