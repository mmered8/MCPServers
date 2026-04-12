"""Unified Grok API client — Chat, Imagine, Collections."""

from dataclasses import dataclass
from typing import Optional

import httpx

GROK_BASE_URL = "https://api.x.ai/v1"

# Pricing per 1M tokens (as of Grok 4.1, March 2026)
PRICING = {
    "grok-3-fast": {"input": 0.20, "output": 0.80},
    "grok-3": {"input": 2.00, "output": 8.00},
    "grok-3-mini": {"input": 0.10, "output": 0.40},
}


@dataclass
class ChatResult:
    text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


@dataclass
class ImagineResult:
    url: str
    cost: float


@dataclass
class CollectionsCreateResult:
    collection_id: str
    tokens_indexed: int


@dataclass
class CollectionsQueryResult:
    text: str
    input_tokens: int
    output_tokens: int


class GrokClient:
    """Async client for xAI's Grok API."""

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._http = httpx.AsyncClient(
            base_url=GROK_BASE_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60.0,
        )

    async def chat(
        self,
        prompt: str,
        model: str = "grok-3-fast",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> ChatResult:
        """Send chat completion request."""
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        resp = await self._http.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        prices = PRICING.get(model, {"input": 0, "output": 0})
        cost = (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1_000_000

        return ChatResult(
            text=choice,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )

    async def imagine(
        self,
        prompt: str,
        model: str = "grok-2-image",
        n: int = 1,
        size: str = "1024x1024",
        format: str = "png",
    ) -> ImagineResult:
        """Generate image via Grok Imagine."""
        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": "url",
        }
        resp = await self._http.post("/images/generations", json=payload)
        resp.raise_for_status()
        data = resp.json()

        url = data["data"][0]["url"]
        # Image generation is flat-rate per image, not token-based
        cost = 0.01 * n  # Approximate cost per image

        return ImagineResult(url=url, cost=cost)

    async def collections_create(
        self,
        name: str,
        documents: list[str],
    ) -> CollectionsCreateResult:
        """Create a document collection for indexing and RAG-style retrieval."""
        payload = {
            "name": name,
            "documents": [{"content": doc} for doc in documents],
        }
        resp = await self._http.post("/collections", json=payload)
        resp.raise_for_status()
        data = resp.json()

        return CollectionsCreateResult(
            collection_id=data["id"],
            tokens_indexed=data.get("tokens_indexed", 0),
        )

    async def collections_query(
        self,
        collection: str,
        query: str,
    ) -> CollectionsQueryResult:
        """Query a document collection for relevant chunks."""
        payload = {"query": query}
        resp = await self._http.post(f"/collections/{collection}/query", json=payload)
        resp.raise_for_status()
        data = resp.json()

        chunks = data.get("results", [])
        text = "\n\n---\n\n".join(
            chunk.get("content", "") for chunk in chunks
        )
        usage = data.get("usage", {})

        return CollectionsQueryResult(
            text=text,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )

    async def close(self):
        await self._http.aclose()
