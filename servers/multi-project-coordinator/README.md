# Multi-Project Coordinator MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![Tests: 19 passing](https://img.shields.io/badge/tests-19%20passing-brightgreen.svg)](#)
[![Transport: streamable-http](https://img.shields.io/badge/transport-streamable--http-purple.svg)](https://spec.modelcontextprotocol.io/)

Manage multiple repos from a single Claude Code session. Track projects, enforce workflows, search across codebases.

**Free & Open Source** | MIT Licensed

## Why This Exists

If you manage 3+ repos, you've felt the pain: open project A, check its status, switch to project B, lose context, forget what project C needs. This server puts all project state in one place — queryable from any Claude Code session in any repo.

Claude Code Agent Teams is official but lacks persistent cross-session project state. This fills that gap.

## Quick Start

This server runs **locally on your machine** — it reads your project markdown files directly from disk.

### 1. Install

```bash
pip install multi-project-coordinator
# or
uv add multi-project-coordinator
```

### 2. Set up your project structure

Point `PROJECTS_ROOT` at a directory containing your project tracking files:

```
your-workspace/          <-- PROJECTS_ROOT points here
├── projects/
│   ├── my-app/
│   │   ├── STATUS.md
│   │   ├── TASKS.md
│   │   └── LOG.md
│   └── my-api/
│       ├── STATUS.md
│       ├── TASKS.md
│       └── LOG.md
├── ideation/
│   └── PIPELINE.md
└── CHANGELOG.md
```

### 3. Start the server

```bash
# Linux/Mac
PROJECTS_ROOT=/path/to/your-workspace python -m multi_project_coordinator

# Windows
set PROJECTS_ROOT=C:\path\to\your-workspace
python -m multi_project_coordinator
```

The server starts on `http://127.0.0.1:8000/mcp` using streamable-http transport.

### 4. Connect from any repo

Add to your `.mcp.json` in any repo:

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

Every Claude Code session now has cross-project awareness.

## Tools

| Tool | What It Does |
|------|-------------|
| `setup_project(name)` | Scaffold a new project with STATUS, TASKS, LOG, MEMORY, and PLAN files |
| `get_dashboard()` | Structured snapshot of all project health, progress, and blockers |
| `get_project_status(project)` | Deep dive into one project — STATUS.md + TASKS.md |
| `get_pipeline()` | Full ideation pipeline — track ideas from raw to shipped |
| `append_log(project, entry)` | Add dated entries to any project's log |
| `update_task(project, task, status)` | Mark tasks done, active, or blocked — confirms exact line matched |
| `session_close(project, summary, changed, next_steps)` | End-of-session wrapper — enforces documentation |
| `search_context(query)` | Full-text search across all markdown files in every project (capped at 50 results) |

## Project Structure

The server expects your projects root to contain:

```
your-projects/
├── projects/
│   ├── project-a/
│   │   ├── STATUS.md      # Health, progress, blockers
│   │   ├── TASKS.md        # Task checklist
│   │   ├── LOG.md          # Session logs (newest first)
│   │   ├── MEMORY.md       # Persistent context
│   │   └── PLAN.md         # Project plan
│   └── project-b/
│       └── ...
├── ideation/
│   └── PIPELINE.md         # Idea pipeline (RAW → EVALUATING → READY → BUILDING)
└── CHANGELOG.md            # Cross-project changelog
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `PROJECTS_ROOT` | *(required)* | Path to your projects root directory |
| `MCP_TRANSPORT` | `streamable-http` | Transport protocol (`streamable-http` or `stdio`) |

## Tech Stack

- Python + FastMCP
- Zero external services (no database, no API keys, no cloud)
- Streamable-http transport (start once, serves all sessions simultaneously)

## License

MIT License. See [LICENSE](LICENSE).

<!-- mcp-name: io.github.mmered8/multi-project-coordinator -->
