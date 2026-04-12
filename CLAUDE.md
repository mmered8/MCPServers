# CLAUDE.md

Guidance for Claude Code and other AI coding tools working on this repository.

## What This Repo Is

Reference implementations of MCP (Model Context Protocol) servers for project coordination. The primary server is `multi-project-coordinator` — a stateful MCP tool that tracks project status, tasks, logs, and an ideation pipeline across multiple sibling repositories.

This is a portfolio / reference repo. The code is meant to be read, forked, and adapted. It's not trying to be a generic library — it's a concrete, working example of a well-structured MCP server you can actually run.

## Tech Stack

- **Python** ≥3.10
- **MCP SDK**: `mcp[cli]` (FastMCP)
- **Transport**: `streamable-http` by default (production pattern for remote MCP), `stdio` via `MCP_TRANSPORT=stdio` for local testing
- **Package manager**: `uv`
- **Testing**: `pytest` with integration tests that exercise each tool end-to-end against a temp project directory

## Repository Structure

```
MCPServers/
├── README.md                          # Public-facing overview
├── CLAUDE.md                          # You are here
├── .gitignore                         # Standard Python template
├── start-server.bat / .sh             # Convenience launchers
└── servers/
    └── multi-project-coordinator/
        ├── src/multi_project_coordinator/
        │   ├── __init__.py
        │   ├── __main__.py            # `python -m multi_project_coordinator`
        │   └── server.py              # FastMCP instance + all 10 tools
        ├── tests/
        │   └── test_server.py         # Integration tests (~20)
        ├── pyproject.toml              # uv package config + metadata
        ├── LICENSE                     # MIT
        ├── server.json                 # MCP Registry submission metadata
        └── README.md
```

All tools live in `server.py` as `@mcp.tool()`-decorated functions. Each tool operates on markdown files under a configurable `PROJECTS_ROOT` directory. Keep tools small, idempotent, and well-tested — each should have at least one happy-path test and one edge-case test (missing file, invalid input, etc.).

## Running Locally

```bash
cd servers/multi-project-coordinator
uv sync                                      # Install deps
PROJECTS_ROOT=/path/to/projects uv run python -m multi_project_coordinator
```

The server starts on `http://127.0.0.1:8000/mcp`. Connect from Claude Code / Cursor via `.mcp.json`:

```json
{
  "mcpServers": {
    "multi-project-coordinator": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

For stdio-mode testing: `MCP_TRANSPORT=stdio uv run python -m multi_project_coordinator`.

## Running Tests

```bash
cd servers/multi-project-coordinator
uv run pytest -v
```

Tests use `tmp_path` fixtures to create an isolated project directory per test, then patch module globals so tools operate on temp files. Never write tests that touch real project files.

## Adding a New Tool

1. Add an `@mcp.tool()`-decorated function to `src/multi_project_coordinator/server.py`. Use a clear docstring — it becomes the tool's description in the MCP client UI.
2. Handle missing files and invalid input gracefully — return a descriptive string instead of raising.
3. Add at least 2 tests to `tests/test_server.py`: one happy path, one edge case.
4. Update the tool table in `README.md`.
5. Run `uv run pytest -v` before committing.

## Design Principles

- **Tools are functions, not classes**. FastMCP works best with plain decorated functions.
- **No hidden state**. Tools read from and write to markdown files directly; no in-memory caches, no ORM.
- **Fail open**. A tool that can't find the project returns a helpful string; it doesn't throw. MCP clients display the response text to the user.
- **Tests use temp directories**. Every test creates its own `PROJECTS_ROOT` so tests are isolated and parallelizable.
- **Streamable-http by default**. Local tools can still use stdio, but production servers (including MCPize-hosted) need HTTP transport.

## License

MIT. Fork freely, adapt freely, attribution appreciated but not required.
