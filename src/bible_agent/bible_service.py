"""
Fixed Bible API Service with better error handling and CORS support.
Place this in: src/bible_agent/bible_service.py
"""

import aiohttp
import logging
from typing import Dict, Optional
from config.bible_config import BibleConfig

logger = logging.getLogger(__name__)


class BibleService:
    """Service for fetching Bible verses from bible-api.com."""
    
    def __init__(self):
        self.config = BibleConfig()
        logger.info(f"📖 Bible API initialized (Translation: {self.config.DEFAULT_TRANSLATION})")
    
    async def get_verse(self, reference: str) -> Optional[Dict]:
        """
        Fetch a Bible verse from the API.
        
        Args:
            reference: Bible reference (e.g., "John 3:16", "Matthew 7:7")
            
        Returns:
            Dict containing verse data or None if failed
        """
        url = self.config.get_verse_url(reference)
        
        logger.info(f"📖 Fetching: {reference}")
        
        try:
            # Create connector with SSL verification disabled for some environments
            # In production, you should handle SSL properly
            connector = aiohttp.TCPConnector(verify_ssl=False)
            timeout = aiohttp.ClientTimeout(total=self.config.TIMEOUT)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as session:
                # Add headers to help with potential CORS/API issues
                headers = {
                    'User-Agent': 'BibleVerseAgent/1.0',
                    'Accept': 'application/json'
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Fetched: {data.get('reference', reference)}")
                        return data
                        
                    elif response.status == 404:
                        logger.warning(f"❌ Verse not found: {reference}")
                        return {
                            "error": "Verse not found",
                            "reference": reference,
                            "message": "Please check the verse reference and try again. Make sure the book name, chapter, and verse are correct."
                        }
                        
                    else:
                        logger.error(f"❌ API error: {response.status}")
                        error_text = await response.text()
                        logger.error(f"Response: {error_text}")
                        return {
                            "error": "API error",
                            "reference": reference,
                            "message": f"The Bible API returned an error (Status: {response.status})"
                        }
                        
        except aiohttp.ClientConnectionError as e:
            logger.error(f"❌ Connection error: {str(e)}")
            return {
                "error": "Connection error",
                "reference": reference,
                "message": "Could not connect to the Bible API. Please check your internet connection."
            }
            
        except aiohttp.ClientTimeout as e:
            logger.error(f"❌ Timeout error: {str(e)}")
            return {
                "error": "Timeout",
                "reference": reference,
                "message": "The Bible API request timed out. Please try again."
            }
            
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
            return {
                "error": "Unexpected error",
                "reference": reference,
                "message": f"An unexpected error occurred: {str(e)}"
            }
    
    async def get_multiple_verses(self, references: list) -> Dict[str, Optional[Dict]]:
        """
        Fetch multiple verses at once.
        
        Args:
            references: List of Bible references
            
        Returns:
            Dict mapping references to their data
        """
        results = {}
        for reference in references:
            results[reference] = await self.get_verse(reference)
        return results
    
    def format_verse_text(self, verse_data: Dict) -> str:
        """
        Format verse data into readable text.
        
        Args:
            verse_data: Verse data from API
            
        Returns:
            Formatted verse text
        """
        if "error" in verse_data:
            return f"❌ {verse_data['message']}"
        
        reference = verse_data.get("reference", "Unknown")
        text = verse_data.get("text", "").strip()
        translation = verse_data.get("translation_name", "King James Version")
        
        return f"""
**{reference}** ({translation})

{text}
        """.strip()