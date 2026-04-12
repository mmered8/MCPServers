# Grok API Wrapper MCP Server

Use xAI's Grok Chat, Imagine, and Collections API from Claude Code — with built-in cost tracking, rate limiting, and response caching.

**$19/mo on [MCPize](https://mcpize.com)** | Proprietary

## Why This Exists

Grok 4.1 Fast is the cheapest major AI API ($0.20/M tokens) but the raw API is clunky. This server makes it seamless from Claude Code:

- **Unified interface** — Chat, image generation, and document indexing through one MCP connection
- **Cost tracking** — Know exactly what you're spending, per-tool breakdown
- **Rate limiting** — Stay within API limits automatically
- **Response caching** — Don't pay twice for the same query

## Tools

| Tool | What It Does |
|------|-------------|
| `grok_chat(prompt, model?, max_tokens?, temperature?)` | Chat completions via Grok API |
| `grok_imagine(prompt, size?, format?)` | Image generation via Grok Imagine |
| `grok_collections_create(name, documents)` | Create a document collection for indexing |
| `grok_collections_query(collection, query)` | Query an existing collection |
| `get_usage()` | Cost tracking summary — total spend, per-tool breakdown |
| `clear_cache()` | Purge the response cache |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `GROK_API_KEY` | *(required)* | Your xAI API key from console.x.ai |
| `GROK_RATE_LIMIT` | `60` | Max requests per minute |
| `GROK_CACHE_TTL` | `3600` | Cache TTL in seconds |
| `MCP_TRANSPORT` | `streamable-http` | Transport protocol |

## Quick Start

```bash
GROK_API_KEY=your-key-here python -m grok_api_wrapper
```

Connect via `.mcp.json`:

```json
{
  "mcpServers": {
    "grok-api-wrapper": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```
