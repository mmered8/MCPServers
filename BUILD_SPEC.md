# Build Spec — Multi-Project Coordinator MCP

## Reference Implementation
A working prototype exists at `../Master_Plan/mcp_server.py` (338 lines, Python, FastMCP).
This server must reproduce and IMPROVE those tools as a publishable MCP package for MCPize ($29/mo).

## Task Queue

Tasks are ordered. Complete them in sequence. Each task is one coding session.
Pick the first task with **Status: READY**. Skip tasks with Status: DONE or BLOCKED.

### TASK-MCP-001: Create project scaffold
**Status**: READY
**What**: Create the Python package structure with pyproject.toml, FastMCP entry point, and a basic test.
**Output**:
- `servers/multi-project-coordinator/pyproject.toml` (uv project, depends on `mcp[cli]`)
- `servers/multi-project-coordinator/src/multi_project_coordinator/__init__.py`
- `servers/multi-project-coordinator/src/multi_project_coordinator/server.py` (FastMCP instance + placeholder tool)
- `servers/multi-project-coordinator/tests/__init__.py`
- `servers/multi-project-coordinator/tests/test_server.py` (basic import test)
**Reference**: `../Master_Plan/mcp_server.py` lines 1-23 (imports, FastMCP setup)
**Acceptance**:
- [ ] `cd servers/multi-project-coordinator && uv sync` succeeds (or pip install -e .)
- [ ] `python -c "from multi_project_coordinator.server import mcp"` imports without error
- [ ] pytest passes
**Commit message**: "feat: scaffold multi-project-coordinator MCP package"

### TASK-MCP-002: Implement get_dashboard tool
**Status**: READY
**Depends on**: TASK-MCP-001
**What**: Port the `_generate_snapshot` + `get_dashboard` tool from the reference.
**Reference**: `../Master_Plan/mcp_server.py` lines 26-153
**Output**: Add tool to `server.py` or create `tools/dashboard.py`
**Acceptance**:
- [ ] Tool registered with `@mcp.tool()` decorator
- [ ] Reads project STATUS.md files, extracts health/progress/blockers
- [ ] Returns structured text summary
- [ ] Test in `tests/test_dashboard.py` passes
**Commit message**: "feat: implement get_dashboard tool"

### TASK-MCP-003: Implement get_project_status tool
**Status**: READY
**Depends on**: TASK-MCP-001
**What**: Port the `get_project_status` tool.
**Reference**: `../Master_Plan/mcp_server.py` lines 156-166
**Output**: Add to server or `tools/project_status.py`
**Acceptance**:
- [ ] Takes project name parameter, validates against available projects
- [ ] Returns STATUS.md + TASKS.md content
- [ ] Test passes
**Commit message**: "feat: implement get_project_status tool"

### TASK-MCP-004: Implement append_log tool
**Status**: READY
**Depends on**: TASK-MCP-001
**What**: Port the `append_log` tool.
**Reference**: `../Master_Plan/mcp_server.py` lines 175-194
**Output**: Add to server or `tools/log.py`
**Acceptance**:
- [ ] Appends dated entry to LOG.md (newest first, after header)
- [ ] Never deletes existing content
- [ ] Test passes
**Commit message**: "feat: implement append_log tool"

### TASK-MCP-005: Implement update_task tool
**Status**: READY
**Depends on**: TASK-MCP-001
**What**: Port the `update_task` tool.
**Reference**: `../Master_Plan/mcp_server.py` lines 197-232
**Output**: Add to server or `tools/tasks.py`
**Acceptance**:
- [ ] Finds task by substring match
- [ ] Supports done/active/blocked status changes with timestamps
- [ ] Test passes
**Commit message**: "feat: implement update_task tool"

### TASK-MCP-006: Implement search_context tool
**Status**: READY
**Depends on**: TASK-MCP-001
**What**: Port the `search_context` tool.
**Reference**: `../Master_Plan/mcp_server.py` lines 304-334
**Output**: Add to server or `tools/search.py`
**Acceptance**:
- [ ] Full-text search across MEMORY.md, LOG.md, PLAN.md
- [ ] Returns file path + line number + context snippet
- [ ] Case-insensitive
- [ ] Test passes
**Commit message**: "feat: implement search_context tool"

### TASK-MCP-007: Implement session_close + get_pipeline + wire all tools
**Status**: READY
**Depends on**: TASK-MCP-004, TASK-MCP-005
**What**: Port remaining tools and ensure all 7 are registered on the FastMCP instance.
**Reference**: `../Master_Plan/mcp_server.py` lines 169-172 (get_pipeline), lines 235-301 (session_close)
**Output**: Complete package with all tools accessible
**Acceptance**:
- [ ] get_pipeline returns PIPELINE.md content
- [ ] session_close appends LOG.md, CHANGELOG.md, regenerates snapshot
- [ ] All 7 tools registered and functional
- [ ] Full test suite passes
- [ ] Server starts: `python -m multi_project_coordinator`
**Commit message**: "feat: complete MCP server with all 7 tools"
