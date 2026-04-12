"""Tests for Grok API Wrapper MCP server."""

import os
import pytest


@pytest.fixture(autouse=True)
def setup_env():
    """Set required env vars for testing."""
    os.environ["GROK_API_KEY"] = "test-key-for-testing"
    yield
    os.environ.pop("GROK_API_KEY", None)


def test_mcp_import():
    """Test that the FastMCP instance can be imported."""
    from grok_api_wrapper.server import mcp
    assert mcp is not None
    assert mcp.name == "grok-api-wrapper"


def test_cost_tracker():
    """Test cost tracking records and summaries."""
    from grok_api_wrapper.cost_tracker import CostTracker

    tracker = CostTracker()
    assert "No API usage" in tracker.summary()

    tracker.record("grok_chat", model="grok-3-fast", input_tokens=1000, output_tokens=500)
    summary = tracker.summary()
    assert "grok_chat" in summary
    assert "1 requests" in summary

    count = tracker.reset()
    assert count == 1
    assert "No API usage" in tracker.summary()


def test_rate_limiter():
    """Test rate limiter initialization."""
    from grok_api_wrapper.rate_limiter import RateLimiter

    limiter = RateLimiter(max_per_minute=60)
    assert limiter._max == 60
    assert limiter._tokens == 60.0


def test_cache():
    """Test response cache set/get/clear."""
    import tempfile
    from grok_api_wrapper.cache import ResponseCache

    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ResponseCache(default_ttl=60, cache_dir=tmpdir)

        key = cache.make_key("chat", prompt="hello")
        assert cache.get(key) is None

        cache.set(key, "world")
        assert cache.get(key) == "world"

        count = cache.clear()
        assert count == 1
        assert cache.get(key) is None

        cache.close()


def test_grok_client_requires_api_key():
    """Test that GrokClient accepts an API key."""
    from grok_api_wrapper.grok_client import GrokClient

    client = GrokClient(api_key="test-key")
    assert client._api_key == "test-key"


# ── Mocked API tests ──────────────────────────────────────


@pytest.mark.asyncio
async def test_grok_chat_mocked():
    """Test grok_chat sends correct request and parses response."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    mock_response = {
        "choices": [{"message": {"content": "Hello from Grok!"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }

    with respx.mock:
        respx.post("https://api.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = GrokClient(api_key="test-key")
        result = await client.chat("Say hello", model="grok-3-fast", temperature=0.7)

        assert result.text == "Hello from Grok!"
        assert result.input_tokens == 10
        assert result.output_tokens == 5
        assert result.cost_usd > 0

        await client.close()


@pytest.mark.asyncio
async def test_grok_chat_api_error():
    """Test grok_chat raises on API error."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(401, json={"error": "Invalid API key"})
        )

        client = GrokClient(api_key="bad-key")
        with pytest.raises(httpx.HTTPStatusError):
            await client.chat("Say hello")
        await client.close()


@pytest.mark.asyncio
async def test_grok_imagine_mocked():
    """Test grok_imagine sends correct request and parses response."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    mock_response = {
        "data": [{"url": "https://example.com/image.png"}],
    }

    with respx.mock:
        respx.post("https://api.x.ai/v1/images/generations").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = GrokClient(api_key="test-key")
        result = await client.imagine("A cat in space")

        assert result.url == "https://example.com/image.png"
        assert result.cost > 0

        await client.close()


@pytest.mark.asyncio
async def test_grok_collections_create_mocked():
    """Test grok_collections_create sends correct request and parses response."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    mock_response = {
        "id": "col_abc123",
        "tokens_indexed": 1500,
    }

    with respx.mock:
        respx.post("https://api.x.ai/v1/collections").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = GrokClient(api_key="test-key")
        result = await client.collections_create(
            "my-docs", ["Document one text", "Document two text"]
        )

        assert result.collection_id == "col_abc123"
        assert result.tokens_indexed == 1500

        await client.close()


@pytest.mark.asyncio
async def test_grok_collections_create_api_error():
    """Test grok_collections_create raises on API error."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/collections").mock(
            return_value=httpx.Response(500, json={"error": "Internal server error"})
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(httpx.HTTPStatusError):
            await client.collections_create("my-docs", ["doc"])
        await client.close()


@pytest.mark.asyncio
async def test_grok_collections_query_mocked():
    """Test grok_collections_query sends correct request and parses response."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    mock_response = {
        "results": [
            {"content": "Relevant chunk one"},
            {"content": "Relevant chunk two"},
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 50},
    }

    with respx.mock:
        respx.post("https://api.x.ai/v1/collections/col_abc123/query").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = GrokClient(api_key="test-key")
        result = await client.collections_query("col_abc123", "search term")

        assert "Relevant chunk one" in result.text
        assert "Relevant chunk two" in result.text
        assert result.input_tokens == 20
        assert result.output_tokens == 50

        await client.close()


@pytest.mark.asyncio
async def test_grok_collections_query_api_error():
    """Test grok_collections_query raises on API error."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/collections/col_bad/query").mock(
            return_value=httpx.Response(404, json={"error": "Collection not found"})
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(httpx.HTTPStatusError):
            await client.collections_query("col_bad", "search")
        await client.close()


@pytest.mark.asyncio
async def test_grok_collections_query_empty_results():
    """Test grok_collections_query handles empty results gracefully."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    mock_response = {
        "results": [],
        "usage": {"prompt_tokens": 10, "completion_tokens": 0},
    }

    with respx.mock:
        respx.post("https://api.x.ai/v1/collections/col_abc123/query").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = GrokClient(api_key="test-key")
        result = await client.collections_query("col_abc123", "no matches")

        assert result.text == ""
        assert result.input_tokens == 10
        assert result.output_tokens == 0

        await client.close()


@pytest.mark.asyncio
async def test_grok_chat_missing_api_key():
    """Test that _init() raises when GROK_API_KEY is not set."""
    import grok_api_wrapper.server as srv

    # Reset lazy-init globals
    srv._client = None
    srv._tracker = None
    srv._limiter = None
    srv._cache = None

    old_key = srv.GROK_API_KEY
    try:
        srv.GROK_API_KEY = None
        with pytest.raises(RuntimeError, match="GROK_API_KEY"):
            srv._init()
    finally:
        srv.GROK_API_KEY = old_key
        # Reset again so other tests aren't affected
        srv._client = None
        srv._tracker = None
        srv._limiter = None
        srv._cache = None


# ── 429 Rate Limit tests ─────────────────────────────────


@pytest.mark.asyncio
async def test_grok_chat_rate_limited():
    """Test grok_chat raises on 429 rate limit response."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(
                429,
                json={"error": {"message": "Rate limit exceeded", "type": "rate_limit_error"}},
            )
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.chat("Say hello")
        assert exc_info.value.response.status_code == 429
        await client.close()


@pytest.mark.asyncio
async def test_grok_imagine_rate_limited():
    """Test grok_imagine raises on 429 rate limit response."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/images/generations").mock(
            return_value=httpx.Response(
                429,
                json={"error": {"message": "Rate limit exceeded"}},
            )
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.imagine("A sunset")
        assert exc_info.value.response.status_code == 429
        await client.close()


@pytest.mark.asyncio
async def test_grok_collections_create_rate_limited():
    """Test grok_collections_create raises on 429 rate limit response."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/collections").mock(
            return_value=httpx.Response(
                429,
                json={"error": {"message": "Rate limit exceeded"}},
            )
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.collections_create("my-docs", ["doc"])
        assert exc_info.value.response.status_code == 429
        await client.close()


@pytest.mark.asyncio
async def test_grok_collections_query_rate_limited():
    """Test grok_collections_query raises on 429 rate limit response."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/collections/col_abc/query").mock(
            return_value=httpx.Response(
                429,
                json={"error": {"message": "Rate limit exceeded"}},
            )
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.collections_query("col_abc", "search")
        assert exc_info.value.response.status_code == 429
        await client.close()


# ── 500 Server Error tests ───────────────────────────────


@pytest.mark.asyncio
async def test_grok_chat_server_error():
    """Test grok_chat raises on 500 server error."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(
                500,
                json={"error": {"message": "Internal server error"}},
            )
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.chat("Say hello")
        assert exc_info.value.response.status_code == 500
        await client.close()


@pytest.mark.asyncio
async def test_grok_imagine_server_error():
    """Test grok_imagine raises on 500 server error."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/images/generations").mock(
            return_value=httpx.Response(
                500,
                json={"error": {"message": "Internal server error"}},
            )
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.imagine("A sunset")
        assert exc_info.value.response.status_code == 500
        await client.close()


# ── Malformed Response tests ─────────────────────────────


@pytest.mark.asyncio
async def test_grok_chat_malformed_response():
    """Test grok_chat raises KeyError on malformed response (missing choices)."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/chat/completions").mock(
            return_value=httpx.Response(200, json={"unexpected": "data"})
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(KeyError):
            await client.chat("Say hello")
        await client.close()


@pytest.mark.asyncio
async def test_grok_imagine_malformed_response():
    """Test grok_imagine raises KeyError on malformed response (missing data)."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/images/generations").mock(
            return_value=httpx.Response(200, json={"unexpected": "data"})
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(KeyError):
            await client.imagine("A sunset")
        await client.close()


@pytest.mark.asyncio
async def test_grok_collections_create_malformed_response():
    """Test grok_collections_create raises KeyError on malformed response (missing id)."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    with respx.mock:
        respx.post("https://api.x.ai/v1/collections").mock(
            return_value=httpx.Response(200, json={"unexpected": "data"})
        )

        client = GrokClient(api_key="test-key")
        with pytest.raises(KeyError):
            await client.collections_create("my-docs", ["doc"])
        await client.close()


@pytest.mark.asyncio
async def test_grok_collections_query_malformed_response():
    """Test grok_collections_query handles malformed response gracefully."""
    import httpx
    import respx
    from grok_api_wrapper.grok_client import GrokClient

    # collections_query uses .get() so missing keys don't raise —
    # instead it returns empty text and zero tokens
    with respx.mock:
        respx.post("https://api.x.ai/v1/collections/col_abc/query").mock(
            return_value=httpx.Response(200, json={"unexpected": "data"})
        )

        client = GrokClient(api_key="test-key")
        result = await client.collections_query("col_abc", "search")
        assert result.text == ""
        assert result.input_tokens == 0
        assert result.output_tokens == 0
        await client.close()
