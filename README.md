# MCPServers

Paid MCP (Model Context Protocol) servers for the [MCPize](https://mcpize.com) marketplace. Each server extends AI coding tools (Claude Code, Cursor, etc.) with custom capabilities.

All servers use **streamable-http** transport by default (the MCPize production standard).

## Servers

### Multi-Project Coordinator ($29/mo)

Cross-repo project state management. Track dashboards, tasks, logs, and pipelines across all your repos from a single AI session.

**Quick start:**

```bash
# Windows
start-server.bat

# Bash
./start-server.sh

# Or manually
PROJECTS_ROOT=/path/to/your/projects python -m multi_project_coordinator
```

`PROJECTS_ROOT` must point to the directory containing your `projects/` and `ideation/` folders (e.g. `Master_Plan/`).

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

**Tools (8):**

| Tool | What It Does |
|------|-------------|
| `setup_project(name)` | Scaffold a new project with all tracking files |
| `get_dashboard()` | Snapshot of all project health, progress, and blockers |
| `get_project_status(project)` | STATUS.md + TASKS.md for one project |
| `get_pipeline()` | Full ideation pipeline (RAW → BUILDING) |
| `append_log(project, entry)` | Add dated log entries (newest first) |
| `update_task(project, task, status)` | Mark tasks done, active, or blocked |
| `session_close(project, summary, changed, next_steps)` | End-of-session documentation enforcement |
| `search_context(query)` | Full-text search across all markdown files in every project |

See [servers/multi-project-coordinator/README.md](servers/multi-project-coordinator/README.md) for full docs.

---

### Grok API Wrapper ($19/mo)
*Coming soon* — Unified interface to Grok Chat, Imagine, and Collections API with cost tracking and caching.

### Landlord Financial ($49/mo)
*Coming soon* — Property cash flow analysis, capex budgeting, deal analysis (IRR/cap rate).
