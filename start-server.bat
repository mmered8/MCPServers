@echo off
REM Start the Multi-Project Coordinator MCP server
REM Serves on http://127.0.0.1:8000/mcp (streamable-http)
REM
REM Usage:
REM   set PROJECTS_ROOT=C:\path\to\your\projects
REM   start-server.bat
REM
REM PROJECTS_ROOT must point to a directory containing projects\<name>\ subfolders
REM (each with STATUS.md, TASKS.md, LOG.md) and optionally ideation\PIPELINE.md.

if "%PROJECTS_ROOT%"=="" (
    echo ERROR: PROJECTS_ROOT environment variable is not set.
    echo.
    echo Set it to a directory containing your projects\ folder, for example:
    echo   set PROJECTS_ROOT=C:\path\to\your\project-root
    echo.
    exit /b 1
)

echo Starting Multi-Project Coordinator MCP server...
echo PROJECTS_ROOT=%PROJECTS_ROOT%
echo Endpoint: http://127.0.0.1:8000/mcp
echo.

cd /d "%~dp0servers\multi-project-coordinator"
uv run python -m multi_project_coordinator
