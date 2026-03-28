# MCPize Listing — Multi-Project Coordinator

## Title
Multi-Project Coordinator MCP Server

## Tagline
Manage multiple repos from a single Claude Code session. Track projects, enforce workflows, search across codebases.

## Price
$9/month

## Description

Stop context-switching between repos. The Multi-Project Coordinator gives Claude Code a unified view of all your projects — status, tasks, logs, and pipeline — through 8 MCP tools.

### Who Is This For

- **Solo founders** running 3-8 repos who lose context between sessions
- **Freelancers** juggling client projects and need cross-project visibility
- **Side-project builders** who want their AI assistant to remember what's blocked across everything
- **Agent operators** running overnight builds that need session handoff between human and machine

### The Problem

Every developer managing 3+ repos has felt it: open project A, check its status, switch to project B, lose context, forget what project C needs. Context vanishes between sessions. There's no single place to ask "what's blocked?" across everything you're building.

Claude Code Agent Teams is official but lacks persistent cross-session project state. This fills that gap.

### Tools Included

| Tool | What It Does |
|------|-------------|
| `setup_project(name)` | Scaffold a new project with STATUS, TASKS, LOG, MEMORY, and PLAN files |
| `get_dashboard()` | Structured snapshot of all project health, progress, and blockers |
| `get_project_status(project)` | Deep dive into one project — STATUS.md + TASKS.md |
| `get_pipeline()` | Full ideation pipeline — track ideas from raw to shipped |
| `append_log(project, entry)` | Add dated entries to any project's log (newest first) |
| `update_task(project, task, status)` | Mark tasks done, active, or blocked — confirms exact line matched |
| `session_close(project, summary, changed, next_steps)` | End-of-session wrapper — enforces documentation discipline |
| `search_context(query)` | Full-text search across all markdown files in every project (capped at 50 results) |

### How It Works

Runs locally on your machine — reads your project markdown files directly from disk. No cloud, no API keys.

1. Install: `pip install multi-project-coordinator`
2. Set `PROJECTS_ROOT` to your workspace (the directory containing your `projects/` folder)
3. Start: `PROJECTS_ROOT=/path/to/workspace python -m multi_project_coordinator`
4. Add to each repo's `.mcp.json`:
   ```json
   { "type": "http", "url": "http://127.0.0.1:8000/mcp" }
   ```
5. Every Claude Code session now has cross-project awareness

Uses streamable-http transport — start once, serves all sessions simultaneously. No subprocess management, no per-repo configuration.

### What You Get

- **Cross-project dashboards**: One tool call shows health, progress, and blockers for every project
- **Session continuity**: `session_close()` enforces logging so the next session (or agent) picks up where you left off
- **Full-text search**: Find anything across all markdown files in every project (STATUS, TASKS, LOG, MEMORY, PLAN, and any custom .md files)
- **Pipeline tracking**: Ideas flow from RAW to EVALUATING to READY to BUILDING — visible from any repo
- **Project scaffolding**: `setup_project()` creates the full file structure so new users aren't lost
- **Zero external services**: No database, no API keys, no cloud. Just Python + your markdown files

### Tech Stack
- Python 3.10+ with FastMCP
- Streamable-http transport (production-ready)
- Zero external services required
- MIT licensed

## Keywords
project management, multi-repo, coordination, task tracking, developer tools, Claude Code, session handoff, cross-project search

## Category
Developer Tools
