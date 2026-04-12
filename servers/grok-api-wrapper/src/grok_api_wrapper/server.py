"""Grok API Wrapper MCP Server.

Wraps xAI's Grok Chat, Imagine, and Collections API with cost tracking,
rate limiting, and response caching. $19/mo on MCPize.
"""

import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

from grok_api_wrapper.grok_client import GrokClient
from grok_api_wrapper.cost_tracker import CostTracker
from grok_api_wrapper.rate_limiter import RateLimiter
from grok_api_wrapper.cache import ResponseCache

# Configuration
GROK_API_KEY = os.environ.get("GROK_API_KEY")
RATE_LIMIT = int(os.environ.get("GROK_RATE_LIMIT", "60"))
CACHE_TTL = int(os.environ.get("GROK_CACHE_TTL", "3600"))

mcp = FastMCP("grok-api-wrapper")

# Initialize components (lazy — created on first tool call)
_client: Optional[GrokClient] = None
_tracker: Optional[CostTracker] = None
_limiter: Optional[RateLimiter] = None
_cache: Optional[ResponseCache] = None


def _init() -> tuple[GrokClient, CostTracker, RateLimiter, ResponseCache]:
    """Initialize all components. Called once on first tool use."""
    global _client, _tracker, _limiter, _cache
    if _client is not None:
        return _client, _tracker, _limiter, _cache

    if not GROK_API_KEY:
        raise RuntimeError(
            "GROK_API_KEY environment variable is required. "
            "Get your key at https://console.x.ai/"
        )

    _client = GrokClient(api_key=GROK_API_KEY)
    _tracker = CostTracker()
    _limiter = RateLimiter(max_per_minute=RATE_LIMIT)
    _cache = ResponseCache(default_ttl=CACHE_TTL)
    return _client, _tracker, _limiter, _cache


# ── Tools ────────────────────────────────────────────────


@mcp.tool()
async def grok_chat(
    prompt: str,
    model: str = "grok-3-fast",
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """Send a chat completion request to Grok API.

    Args:
        prompt: The message to send
        model: Grok model to use (grok-3-fast, grok-3, grok-3-mini)
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0.0 to 2.0)
    """
    client, tracker, limiter, cache = _init()

    cache_key = cache.make_key("chat", prompt=prompt, model=model, max_tokens=max_tokens, temperature=temperature)
    cached = cache.get(cache_key)
    if cached:
        return f"[cached] {cached}"

    await limiter.acquire()
    result = await client.chat(prompt, model=model, max_tokens=max_tokens, temperature=temperature)
    tracker.record("grok_chat", model=model, input_tokens=result.input_tokens, output_tokens=result.output_tokens)
    cache.set(cache_key, result.text)
    return result.text


@mcp.tool()
async def grok_imagine(
    prompt: str,
    model: str = "grok-2-image",
    n: int = 1,
    size: str = "1024x1024",
) -> str:
    """Generate an image using Grok Imagine.

    Args:
        prompt: Description of the image to generate
        model: Image model to use (grok-2-image)
        n: Number of images to generate
        size: Image dimensions (1024x1024, 512x512)
    """
    client, tracker, limiter, cache = _init()
    await limiter.acquire()
    result = await client.imagine(prompt, model=model, n=n, size=size)
    tracker.record("grok_imagine", model=model, cost_override=result.cost)
    return f"Image generated: {result.url}"


@mcp.tool()
async def grok_collections_create(name: str, documents: list[str]) -> str:
    """Create a document collection for indexing and search.

    Args:
        name: Name for the collection
        documents: List of document texts to index
    """
    client, tracker, limiter, cache = _init()
    await limiter.acquire()
    result = await client.collections_create(name, documents)
    tracker.record("grok_collections_create", model="collections", input_tokens=result.tokens_indexed)
    return f"Collection '{name}' created with {len(documents)} documents ({result.tokens_indexed} tokens indexed)"


@mcp.tool()
async def grok_collections_query(collection: str, query: str) -> str:
    """Query an existing document collection.

    Args:
        collection: Collection name to search
        query: Search query
    """
    client, tracker, limiter, cache = _init()

    cache_key = cache.make_key("collections_query", collection=collection, query=query)
    cached = cache.get(cache_key)
    if cached:
        return f"[cached] {cached}"

    await limiter.acquire()
    result = await client.collections_query(collection, query)
    tracker.record("grok_collections_query", model="collections", input_tokens=result.input_tokens, output_tokens=result.output_tokens)
    cache.set(cache_key, result.text)
    return result.text


@mcp.tool()
def get_usage() -> str:
    """Get cost tracking summary — total spend, per-tool breakdown, request counts."""
    _, tracker, _, _ = _init()
    return tracker.summary()


@mcp.tool()
def clear_cache() -> str:
    """Purge the response cache."""
    _, _, _, cache = _init()
    count = cache.clear()
    return f"Cache cleared ({count} entries removed)"


def main():
    transport = os.environ.get("MCP_TRANSPORT", "streamable-http")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
