# MCPServers

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](servers/multi-project-coordinator/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/MCP-streamable--http-purple.svg)](https://spec.modelcontextprotocol.io/)

Reference implementations of MCP (Model Context Protocol) servers for project coordination. Built to show how MCP servers are structured, tested, and packaged — and to solve a real problem I had managing state across multiple repos from Claude Code sessions.

Transport: **streamable-http** (the production MCPize standard), configurable via `MCP_TRANSPORT=stdio` for local testing.

## Multi-Project Coordinator

If you manage 3+ repos and have felt the pain of losing context every time you switch projects, this server puts all of your project state (status, tasks, logs, ideation pipeline) in one queryable place — readable from any Claude Code or Cursor session in any repo.

**Quick start:**

```bash
# Windows
start-server.bat

# Bash
./start-server.sh

# Or manually
PROJECTS_ROOT=/path/to/your/projects python -m multi_project_coordinator
```

`PROJECTS_ROOT` must point to a directory containing `projects/<name>/` subfolders (each with `STATUS.md`, `TASKS.md`, `LOG.md`, etc.) and an optional `ideation/PIPELINE.md`.

**Connect from any repo** — add to `.mcp.json`:

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

**Tools (10):**

| Tool | What It Does |
|------|-------------|
| `setup_project(name)` | Scaffold a new project with all tracking files |
| `get_dashboard()` | Snapshot of all project health, progress, and blockers |
| `get_project_status(project)` | `STATUS.md` + `TASKS.md` for one project |
| `get_pipeline()` | Full ideation pipeline (RAW → BUILDING) |
| `append_log(project, entry)` | Add dated log entries (newest first) |
| `update_task(project, task, status)` | Mark tasks done, active, or blocked |
| `create_task(project, task, section)` | Add new tasks programmatically |
| `session_close(project, summary, changed, next_steps)` | End-of-session documentation enforcement |
| `search_context(query)` | Full-text search across all markdown files in every project |
| `get_git_status(project)` | Branch, uncommitted count, last commit age for a project's repo |

See [servers/multi-project-coordinator/README.md](servers/multi-project-coordinator/README.md) for full tool reference, install notes, and testing.

## Repository Layout

```
MCPServers/
├── README.md                          # You are here
├── servers/
│   └── multi-project-coordinator/     # The reference server
│       ├── src/multi_project_coordinator/
│       │   └── server.py              # FastMCP instance + 10 tools
│       ├── tests/test_server.py       # ~20 integration tests
│       ├── pyproject.toml             # uv package config
│       └── README.md
├── start-server.bat                   # Windows launcher
└── start-server.sh                    # Bash launcher
```

## Running Tests

```bash
cd servers/multi-project-coordinator
uv sync
uv run pytest -v
```

## Why This Repo Exists

Two reasons:
1. **Solved a real problem for me**: I manage several repos in parallel and Claude Code / Cursor sessions kept losing cross-repo context. This server fixes that.
2. **Reference implementation**: Shows the full MCP server build pattern — FastMCP, streamable-http transport, proper packaging with `uv`, integration tests, `pyproject.toml` metadata for registry submission, streamable-http + stdio dual transport.

Feel free to fork, adapt, or use as a starting point for your own MCP server.

## License

MIT — see [LICENSE](servers/multi-project-coordinator/LICENSE).
