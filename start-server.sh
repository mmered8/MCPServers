#!/usr/bin/env bash
# Start the Multi-Project Coordinator MCP server
# Serves on http://127.0.0.1:8000/mcp (streamable-http)
#
# Usage:
#   export PROJECTS_ROOT=/path/to/your/projects
#   ./start-server.sh
#
# PROJECTS_ROOT must point to a directory containing projects/<name>/ subfolders
# (each with STATUS.md, TASKS.md, LOG.md) and optionally ideation/PIPELINE.md.

if [ -z "$PROJECTS_ROOT" ]; then
    echo "ERROR: PROJECTS_ROOT environment variable is not set."
    echo
    echo "Set it to a directory containing your projects/ folder, for example:"
    echo "  export PROJECTS_ROOT=/path/to/your/project-root"
    echo
    exit 1
fi

echo "Starting Multi-Project Coordinator MCP server..."
echo "PROJECTS_ROOT=$PROJECTS_ROOT"
echo "Endpoint: http://127.0.0.1:8000/mcp"
echo

cd "$(dirname "$0")/servers/multi-project-coordinator"
uv run python -m multi_project_coordinator
