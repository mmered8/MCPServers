# CHANGELOG — MCPServers

Reverse-chronological session history. One entry per meaningful work session.

---

## [2026-03-29] — Strategic pivot: multi-project-coordinator goes free/OSS

- Repositioned `multi-project-coordinator` as free/open-source to drive adoption and inbound
- `grok-api-wrapper` becomes the paid product on MCPize marketplace
- Removed internal files from public repo (BUILD_SPEC.md, internal docs)
- Fixed stale docstrings left over from pre-pivot wording

## [2026-03-28] — Marketplace launch prep + MCP Registry registration

- Added `server.json` for MCP Registry listing (official MCP discovery index)
- Added PyPI verification tag to README
- Polished pricing copy: $9/mo listing, README badges added
- Updated marketplace listing copy for MCPize submission

## [2026-03-28] — Multi-Project Coordinator v1 complete

- Built complete Multi-Project Coordinator MCP server (7 tools):
  - `get_dashboard` — regenerates and returns STATUS_SNAPSHOT
  - `get_project_status` — returns STATUS.md + TASKS.md for any project
  - `get_pipeline` — full ideation pipeline read
  - `append_log` — dated log entry append
  - `update_task` — mark tasks done/active/blocked
  - `session_close` — enforces close-the-loop rule
  - `search_context` — full-text search across MEMORY.md, LOG.md, PLAN.md
- 12/12 tests passing
- Security hardening: path traversal vulnerability patched
- 19/19 total tests passing after security audit
- Marketplace-ready: README, pricing, listing copy finalized

## [2026-03-24] — Project scaffold

- Initial commit: `CLAUDE.md`, `BUILD_SPEC.md`
- Defined repo structure: `servers/`, `docs/`, `launch/`
- Established build targets and acceptance criteria
