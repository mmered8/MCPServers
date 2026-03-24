# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Build and sell **paid MCP (Model Context Protocol) servers** on the MCPize marketplace. MCP servers extend AI coding tools (Claude Code, Cursor, etc.) with custom capabilities. This is a revenue-generating product repo.

**Business model**: MCPize takes 15%, you keep 85%. Pricing: $19-149/mo per subscriber. Real revenue examples on MCPize: PostgreSQL Connector earns $4,200/mo (207 subs at $29/mo), AWS Security Auditor earns $8,500/mo (82 enterprise subs at $149/mo).

**Market opportunity**: 18,500+ MCP servers exist but less than 5% are monetized. Massive greenfield for paid servers that solve real problems.

## Tech Stack

- **Language**: Python (preferred) or TypeScript
- **MCP SDK**: `mcp` Python package or `@modelcontextprotocol/sdk` for TypeScript
- **Testing**: pytest for Python, vitest for TypeScript
- **Publishing**: MCPize (primary), MCP Hive (launching May 11, 2026), list on MCP.so and PulseMCP for visibility

## MCP Servers to Build (Priority Order)

### 1. Multi-Project Coordinator MCP
**Target**: Developers managing multiple repos with Claude Code
**Price**: $29/mo
**What it does**: Read/update STATUS.md, TASKS.md, METRICS.md, LOG.md across multiple project directories. Aggregate dashboards. Cross-project search. Session handoff notes.
**Why it sells**: Claude Code Agent Teams is official but lacks persistent cross-session project state. This fills that gap.

### 2. Grok API Wrapper MCP
**Target**: Developers using xAI's Grok API
**Price**: $19/mo
**What it does**: Unified interface to Grok Chat, Grok Imagine (video/image gen), and Collections API (document indexing). Built-in cost tracking, rate limiting, response caching. Usage dashboard.
**Why it sells**: Grok 4.1 Fast is cheapest major AI API ($0.20/M tokens) but raw API is clunky. This makes it seamless from Claude Code.
**Config needed**: Grok API key (user provides their own)

### 3. Landlord Financial MCP
**Target**: Landlord-developers, property managers
**Price**: $49/mo
**What it does**: Property cash flow analysis, rent tracking, capex budgeting, deal analysis (IRR/cap rate), maintenance cost forecasting. Connects to Plaid for bank data.
**Why it sells**: Synergy with the LandlordAdvisor project. MCP version lets Claude Code do property analysis inline.

## Repository Structure

```
MCPServers/
├── CLAUDE.md
├── README.md
├── .gitignore
├── servers/
│   ├── multi-project-coordinator/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── README.md
│   ├── grok-api-wrapper/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── README.md
│   └── landlord-financial/
│       ├── src/
│       ├── tests/
│       ├── pyproject.toml
│       └── README.md
└── shared/
    └── utils/           # Shared utilities across servers
```

## Development Workflow

1. Each server is a standalone Python package in `servers/`
2. Use `uv` for dependency management (fast, modern)
3. Each server should have its own tests, README, and pyproject.toml
4. Test locally with Claude Code before publishing
5. Publish to MCPize via their developer portal

## Key Links

- MCPize Developer Portal: https://mcpize.com/developers/monetize-mcp-servers
- MCP Protocol Spec: https://spec.modelcontextprotocol.io/
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- MCP Hive (Founding Provider signup): https://mcp-hive.com/
- MCP.so Directory: https://mcp.so/
- PulseMCP Directory: https://www.pulsemcp.com/servers

## Coordination

- This project is tracked in `../Master_Plan/projects/mcp-servers/`
- Pipeline entry: `../Master_Plan/ideation/PIPELINE.md` — Idea N
- Market research: `../Master_Plan/ideation/market-signals/trends.md` — MCP Server Marketplace section
- Owner has existing MCP experience (2.5 years context engineering, MCP scaffolding)
