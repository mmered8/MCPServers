"""TTL-based response cache using diskcache for persistence."""

import hashlib
import json
from typing import Any, Optional

import diskcache


class ResponseCache:
    """Persistent TTL cache for API responses."""

    def __init__(self, default_ttl: int = 3600, cache_dir: str = ".grok_cache"):
        self._ttl = default_ttl
        self._cache = diskcache.Cache(cache_dir)

    def make_key(self, tool: str, **params: Any) -> str:
        """Create a cache key from tool name and params."""
        raw = json.dumps({"tool": tool, **params}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, key: str) -> Optional[str]:
        """Get cached response, or None if expired/missing."""
        return self._cache.get(key)

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Cache a response with TTL."""
        self._cache.set(key, value, expire=ttl or self._ttl)

    def clear(self) -> int:
        """Clear all cached responses. Returns count of entries removed."""
        count = len(self._cache)
        self._cache.clear()
        return count

    def close(self):
        self._cache.close()
