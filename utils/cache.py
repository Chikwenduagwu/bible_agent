"""
Fixed async cache manager.
REPLACE your utils/cache.py with this file.
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Async file-based cache manager with TTL support."""
    
    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 168):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live in hours (default: 168 = 7 days)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600
        logger.info(f"💾 Cache initialized: {cache_dir} (TTL: {ttl_hours}h)")
    
    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path from key."""
        # Use SHA-256 hash as filename for safety
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    async def get(self, key: str) -> Optional[dict]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_file = self._get_cache_path(key)
        
        if not cache_file.exists():
            return None
        
        try:
            # Check if expired
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age > self.ttl_seconds:
                logger.info(f"🗑️ Cache expired: {key[:20]}...")
                cache_file.unlink()
                return None
            
            # Read and return cached data
            data = json.loads(cache_file.read_text())
            logger.info(f"✅ Cache hit: {key[:20]}... (age: {file_age:.0f}s)")
            return data
            
        except Exception as e:
            logger.error(f"❌ Cache read error: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any) -> bool:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_file = self._get_cache_path(key)
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to cache
            cache_file.write_text(json.dumps(value, indent=2))
            logger.info(f"💾 Cached: {key[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache write error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        cache_file = self._get_cache_path(key)
        if cache_file.exists():
            cache_file.unlink()
            logger.info(f"🗑️ Cache deleted: {key[:20]}...")
            return True
        return False
    
    def clear_all(self) -> int:
        """Clear all cache entries."""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        logger.info(f"🗑️ Cleared {count} cache entries")
        return count