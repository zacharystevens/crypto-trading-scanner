#!/usr/bin/env python3
"""
CachingService - Handles caching of analysis results and market data
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CachingService:
    """Service responsible for caching analysis results and market data"""
    
    def __init__(self):
        # In-memory cache storage
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Cache configuration
        self.DEFAULT_TTL = 900  # 15 minutes default
        self.TICKER_CACHE_TTL = 60  # 1 minute for ticker data
        self.ANALYSIS_CACHE_TTL = 900  # 15 minutes for analysis results
        self.OHLCV_CACHE_TTL = 300  # 5 minutes for OHLCV data
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'expired': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if key not in self._cache:
                self.stats['misses'] += 1
                logger.debug(f"Cache miss for key: {key}")
                return None
            
            cache_entry = self._cache[key]
            
            # Check if expired
            if self._is_expired(cache_entry):
                self.delete(key)
                self.stats['expired'] += 1
                logger.debug(f"Cache expired for key: {key}")
                return None
            
            self.stats['hits'] += 1
            logger.debug(f"Cache hit for key: {key}")
            return cache_entry['data']
            
        except Exception as e:
            logger.error(f"Error getting cache value for {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            ttl = ttl or self.DEFAULT_TTL
            expiry_time = time.time() + ttl
            
            self._cache[key] = {
                'data': value,
                'timestamp': time.time(),
                'expires_at': expiry_time,
                'ttl': ttl
            }
            
            self.stats['sets'] += 1
            logger.debug(f"Cache set for key: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache value for {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if key in self._cache:
                del self._cache[key]
                self.stats['deletes'] += 1
                logger.debug(f"Cache deleted for key: {key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting cache value for {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cache cleared: {count} entries removed")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def clear_expired(self) -> int:
        """Clear all expired entries and return count"""
        try:
            expired_keys = []
            current_time = time.time()
            
            for key, cache_entry in self._cache.items():
                if current_time > cache_entry['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.info(f"Cleared {len(expired_keys)} expired cache entries")
                self.stats['expired'] += len(expired_keys)
            
            return len(expired_keys)
            
        except Exception as e:
            logger.error(f"Error clearing expired cache entries: {e}")
            return 0
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all cache entries matching pattern"""
        try:
            matching_keys = [key for key in self._cache.keys() if pattern in key]
            
            for key in matching_keys:
                del self._cache[key]
            
            if matching_keys:
                logger.info(f"Cleared {len(matching_keys)} cache entries matching pattern: {pattern}")
                self.stats['deletes'] += len(matching_keys)
            
            return len(matching_keys)
            
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        return time.time() > cache_entry['expires_at']
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_entries': len(self._cache),
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': round(hit_rate, 2),
            'sets': self.stats['sets'],
            'deletes': self.stats['deletes'],
            'expired': self.stats['expired']
        }
    
    def get_cache_info(self) -> List[Dict[str, Any]]:
        """Get information about cached entries"""
        try:
            cache_info = []
            current_time = time.time()
            
            for key, cache_entry in self._cache.items():
                age_seconds = int(current_time - cache_entry['timestamp'])
                ttl_remaining = int(cache_entry['expires_at'] - current_time)
                
                cache_info.append({
                    'key': key,
                    'age_seconds': age_seconds,
                    'ttl_remaining': ttl_remaining,
                    'expired': ttl_remaining <= 0,
                    'size_bytes': len(str(cache_entry['data']))  # Rough size estimate
                })
            
            return sorted(cache_info, key=lambda x: x['age_seconds'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return []
    
    # Convenience methods for specific cache types
    
    def get_ticker_data(self, key: str) -> Optional[Any]:
        """Get ticker data from cache"""
        return self.get(f"ticker:{key}")
    
    def set_ticker_data(self, key: str, data: Any) -> bool:
        """Set ticker data in cache"""
        return self.set(f"ticker:{key}", data, self.TICKER_CACHE_TTL)
    
    def get_analysis_result(self, symbol: str, analysis_type: str) -> Optional[Any]:
        """Get analysis result from cache"""
        cache_key = f"analysis:{symbol}:{analysis_type}"
        return self.get(cache_key)
    
    def set_analysis_result(self, symbol: str, analysis_type: str, result: Any) -> bool:
        """Set analysis result in cache"""
        cache_key = f"analysis:{symbol}:{analysis_type}"
        return self.set(cache_key, result, self.ANALYSIS_CACHE_TTL)
    
    def get_ohlcv_data(self, symbol: str, timeframe: str) -> Optional[Any]:
        """Get OHLCV data from cache"""
        cache_key = f"ohlcv:{symbol}:{timeframe}"
        return self.get(cache_key)
    
    def set_ohlcv_data(self, symbol: str, timeframe: str, data: Any) -> bool:
        """Set OHLCV data in cache"""
        cache_key = f"ohlcv:{symbol}:{timeframe}"  
        return self.set(cache_key, data, self.OHLCV_CACHE_TTL)
    
    def get_curated_coins(self) -> Optional[Any]:
        """Get curated coins data from cache"""
        return self.get("curated_30_coins")
    
    def set_curated_coins(self, data: Any) -> bool:
        """Set curated coins data in cache"""
        return self.set("curated_30_coins", data, self.ANALYSIS_CACHE_TTL)
    
    def invalidate_symbol_cache(self, symbol: str) -> int:
        """Invalidate all cache entries for a specific symbol"""
        return self.clear_pattern(symbol) 