"""Token bucket rate limiter for Grok API calls."""

import asyncio
import time


class RateLimiter:
    """Async token bucket rate limiter."""

    def __init__(self, max_per_minute: int = 60):
        self._max = max_per_minute
        self._tokens = float(max_per_minute)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a request token is available."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self._max, self._tokens + elapsed * (self._max / 60.0))
            self._last_refill = now

            if self._tokens < 1.0:
                wait_time = (1.0 - self._tokens) / (self._max / 60.0)
                await asyncio.sleep(wait_time)
                self._tokens = 0.0
            else:
                self._tokens -= 1.0
