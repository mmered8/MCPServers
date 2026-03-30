"""Multi-Project Coordinator MCP Server.

Exposes tools for Claude Code sessions to query business state,
update project tracking, and enforce the close-the-loop rule across
multiple project directories.

Free & open source. Streamable-http transport.
"""

import os
import re
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Configuration: project root from environment (required)
# Resolved lazily so tests can set PROJECTS_ROOT before first tool call.
PROJECTS_ROOT: Path = None  # type: ignore[assignment]
PROJECTS_DIR: Path = None  # type: ignore[assignment]
IDEATION_DIR: Path = None  # type: ignore[assignment]


def _init_paths() -> None:
    """Resolve PROJECTS_ROOT from environment. Called once on first tool use."""
    global PROJECTS_ROOT, PROJECTS_DIR, IDEATION_DIR
    if PROJECTS_ROOT is not None:
        return
    root = os.environ.get("PROJECTS_ROOT")
    if not root:
        raise RuntimeError(
            "PROJECTS_ROOT environment variable is required. "
            "Set it to the directory containing your projects/ and ideation/ folders. "
            "Example: PROJECTS_ROOT=/path/to/workspace python -m multi_project_coordinator"
        )
    PROJECTS_ROOT = Path(root)
    if not PROJECTS_ROOT.exists():
        raise RuntimeError(f"PROJECTS_ROOT directory does not exist: {PROJECTS_ROOT}")
    PROJECTS_DIR = PROJECTS_ROOT / "projects"
    IDEATION_DIR = PROJECTS_ROOT / "ideation"

mcp = FastMCP("multi-project-coordinator")


# ── Helpers ──────────────────────────────────────────────


def _read_file(path: Path) -> str:
    """Read a file, return informative message if missing."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"(file not found: {path.name})"


def _valid_project(project: str) -> Path:
    """Validate project name and return its directory."""
    _init_paths()
    if ".." in project or "/" in project or "\\" in project:
        raise ValueError(
            f"Invalid project name '{project}'. "
            "Project names cannot contain path separators or '..'."
        )
    project_dir = PROJECTS_DIR / project
    if not project_dir.exists():
        available = [
            d.name for d in PROJECTS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ]
        raise ValueError(
            f"Project '{project}' not found. "
            f"Available: {', '.join(sorted(available))}"
        )
    return project_dir


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _datestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ── Tools ────────────────────────────────────────────────


@mcp.tool()
def setup_project(name: str) -> str:
    """Create a new project with the standard tracking file structure.

    Scaffolds STATUS.md, TASKS.md, LOG.md, MEMORY.md, and PLAN.md
    in a new project directory under projects/.

    Args:
        name: Project folder name (lowercase, hyphens ok, e.g. 'my-new-app')
    """
    _init_paths()
    if ".." in name or "/" in name or "\\" in name:
        raise ValueError("Project name cannot contain path separators or '..'.")
    if not re.match(r"^[a-z0-9][a-z0-9-]*$", name):
        raise ValueError(
            f"Invalid project name '{name}'. "
            "Use lowercase letters, numbers, and hyphens (e.g. 'my-app')."
        )

    project_dir = PROJECTS_DIR / name
    if project_dir.exists():
        raise ValueError(f"Project '{name}' already exists.")

    project_dir.mkdir(parents=True)
    today = _datestamp()
    title = name.replace("-", " ").title()

    (project_dir / "STATUS.md").write_text(
        f"# {title} — Status\n\n"
        f"- Health: GREY\n"
        f"- Overall progress: 0%\n"
        f"- Blocker: None\n"
        f"- Started: {today}\n",
        encoding="utf-8",
    )
    (project_dir / "TASKS.md").write_text(
        f"# {title} — Tasks\n\n## Active\n\n- [ ] Define project scope\n\n## Completed\n\n",
        encoding="utf-8",
    )
    (project_dir / "LOG.md").write_text(
        f"# {title} — Log\n\n## {today}\n\nProject created.\n",
        encoding="utf-8",
    )
    (project_dir / "MEMORY.md").write_text(
        f"# {title} — Memory\n\nKey decisions and context go here.\n",
        encoding="utf-8",
    )
    (project_dir / "PLAN.md").write_text(
        f"# {title} — Plan\n\nHigh-level plan goes here.\n",
        encoding="utf-8",
    )

    return (
        f"Created project '{name}' at {project_dir}\n"
        f"Files: STATUS.md, TASKS.md, LOG.md, MEMORY.md, PLAN.md"
    )


@mcp.tool()
def get_dashboard() -> str:
    """Get the current business state as a structured snapshot.

    Scans all project STATUS.md files and returns a machine-readable
    summary of health, progress, and blockers for every project.
    Also includes pipeline stage counts and last session date.
    """
    _init_paths()
    lines = [
        "# Status Snapshot",
        f"# Auto-generated by multi-project-coordinator MCP",
        f"# Last updated: {datetime.now().isoformat(timespec='minutes')}",
        "",
        "## PROJECTS",
        "",
    ]

    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith("_"):
            continue

        status_file = project_dir / "STATUS.md"
        if not status_file.exists():
            continue

        content = status_file.read_text(encoding="utf-8")
        name = project_dir.name.replace("-", " ").title()
        health = "UNKNOWN"
        progress = "UNKNOWN"
        blocker = "None"

        for line in content.splitlines():
            line_lower = line.lower()
            if "health" in line_lower and ":" in line:
                health_match = re.search(r"(GREEN|YELLOW|RED|GREY)", line, re.I)
                if health_match:
                    health = health_match.group(1).upper()
            if "progress" in line_lower or "overall" in line_lower:
                pct_match = re.search(r"(\d+)%", line)
                if pct_match:
                    progress = f"{pct_match.group(1)}%"
            if "blocker" in line_lower and ":" in line:
                blocker = line.split(":", 1)[1].strip() or "None"

        lines.append(f"PROJECT: {name}")
        lines.append(f"HEALTH: {health}")
        lines.append(f"PROGRESS: {progress}")
        lines.append(f"BLOCKER: {blocker}")
        lines.append("")

    # Pipeline summary
    pipeline_file = IDEATION_DIR / "PIPELINE.md"
    if pipeline_file.exists():
        pipeline = pipeline_file.read_text(encoding="utf-8")
        sections = re.split(r"^## ", pipeline, flags=re.M)
        counts = {}
        for section in sections:
            first_line = section.split("\n")[0].strip()
            idea_count = len(re.findall(r"^### ", section, re.M))
            for stage in ["BUILDING", "READY", "EVALUATING", "RAW"]:
                if stage in first_line:
                    counts[stage] = idea_count

        lines.append("## PIPELINE")
        for stage in ["BUILDING", "READY", "EVALUATING", "RAW"]:
            lines.append(f"{stage}: {counts.get(stage, 0)}")
        lines.append("")

    # Last session from changelog
    changelog = PROJECTS_ROOT / "CHANGELOG.md"
    if changelog.exists():
        cl_content = changelog.read_text(encoding="utf-8")
        date_match = re.search(r"^## (\d{4}-\d{2}-\d{2})", cl_content, re.M)
        if date_match:
            lines.append("## LAST_SESSION")
            lines.append(f"DATE: {date_match.group(1)}")
            lines.append("")

    return "\n".join(lines)


@mcp.tool()
def get_project_status(project: str) -> str:
    """Get STATUS.md and TASKS.md for a specific project.

    Args:
        project: Project folder name (e.g., 'budget-revolution', 'mcp-servers')
    """
    project_dir = _valid_project(project)
    status = _read_file(project_dir / "STATUS.md")
    tasks = _read_file(project_dir / "TASKS.md")
    return f"# {project} — Status\n\n{status}\n\n---\n\n# {project} — Tasks\n\n{tasks}"


@mcp.tool()
def get_pipeline() -> str:
    """Get the full ideation pipeline — all ideas and their stages."""
    _init_paths()
    return _read_file(IDEATION_DIR / "PIPELINE.md")


@mcp.tool()
def append_log(project: str, entry: str) -> str:
    """Append a dated entry to a project's LOG.md (newest first).

    Args:
        project: Project folder name
        entry: The log entry text (date is added automatically)
    """
    project_dir = _valid_project(project)
    log_file = project_dir / "LOG.md"
    title = project.replace("-", " ").title()

    if not log_file.exists():
        log_file.write_text(f"# {title} — Log\n", encoding="utf-8")
    existing = log_file.read_text(encoding="utf-8")

    header_end = existing.find("\n") + 1
    header = existing[:header_end]
    body = existing[header_end:]

    new_entry = f"\n## {_datestamp()}\n\n{entry}\n"
    log_file.write_text(header + new_entry + body, encoding="utf-8")
    return f"Appended to {project}/LOG.md at {_timestamp()}"


@mcp.tool()
def update_task(project: str, task: str, status: str) -> str:
    """Update a task's status in a project's TASKS.md.

    Args:
        project: Project folder name
        task: The task description (or substring to match)
        status: New status — 'done', 'active', 'blocked', or 'remove'
    """
    project_dir = _valid_project(project)
    tasks_file = project_dir / "TASKS.md"
    content = _read_file(tasks_file)

    lines = content.splitlines()
    found_line = None
    original_text = None
    for i, line in enumerate(lines):
        if task.lower() in line.lower():
            original_text = line.strip()
            if status == "done":
                lines[i] = re.sub(r"^- \[ \]", "- [x]", line)
                if "completed" not in line.lower():
                    lines[i] += f" — _completed {_datestamp()}_"
            elif status == "active":
                lines[i] = re.sub(r"^- \[x\]", "- [ ]", line)
            elif status == "blocked":
                if "blocked" not in line.lower():
                    lines[i] += " — _blocked_"
            found_line = i + 1
            break

    if found_line is None:
        return f"Task matching '{task}' not found in {project}/TASKS.md"

    tasks_file.write_text("\n".join(lines), encoding="utf-8")
    return (
        f"Updated task in {project}/TASKS.md (line {found_line}): "
        f"'{original_text}' → {status}"
    )


@mcp.tool()
def search_context(query: str) -> str:
    """Full-text search across all markdown files in every project.

    Searches STATUS.md, TASKS.md, LOG.md, MEMORY.md, PLAN.md,
    and any other .md files found in project directories.
    Returns up to 50 matches with surrounding context.

    Args:
        query: Search term (case-insensitive)
    """
    _init_paths()
    results = []
    max_results = 50

    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith("_"):
            continue
        for filepath in sorted(project_dir.glob("*.md")):
            content = filepath.read_text(encoding="utf-8")
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if query.lower() in line.lower():
                    context_start = max(0, i - 1)
                    context_end = min(len(lines), i + 2)
                    snippet = "\n".join(lines[context_start:context_end])
                    results.append(
                        f"**{project_dir.name}/{filepath.name}** (line {i + 1}):\n{snippet}"
                    )
                    if len(results) >= max_results:
                        break
            if len(results) >= max_results:
                break
        if len(results) >= max_results:
            break

    if not results:
        return f"No matches for '{query}' across project files."
    truncated = f" (showing first {max_results})" if len(results) >= max_results else ""
    return f"Found {len(results)} match(es) for '{query}'{truncated}:\n\n" + "\n\n---\n\n".join(results)


@mcp.tool()
def session_close(project: str, summary: str, changed: str, next_steps: str) -> str:
    """Close the loop on a session. Enforces the close-the-loop rule.

    Appends to the project's LOG.md, appends to CHANGELOG.md,
    and regenerates the dashboard snapshot.

    Args:
        project: Primary project worked on
        summary: 1-2 sentence summary of what was done
        changed: Files or features that changed
        next_steps: What the next session should do
    """
    # 1. Append to project LOG.md
    project_dir = _valid_project(project)
    log_file = project_dir / "LOG.md"
    title = project.replace("-", " ").title()
    if not log_file.exists():
        log_file.write_text(f"# {title} — Log\n", encoding="utf-8")
    existing_log = log_file.read_text(encoding="utf-8")
    header_end = existing_log.find("\n") + 1

    log_entry = (
        f"\n## {_datestamp()}\n\n"
        f"**Summary**: {summary}\n"
        f"**Changed**: {changed}\n"
        f"**Next**: {next_steps}\n"
    )
    log_file.write_text(
        existing_log[:header_end] + log_entry + existing_log[header_end:],
        encoding="utf-8",
    )

    # 2. Append to CHANGELOG.md
    changelog = PROJECTS_ROOT / "CHANGELOG.md"
    if not changelog.exists():
        changelog.write_text("# Changelog\n", encoding="utf-8")
    cl_content = changelog.read_text(encoding="utf-8")

    today = _datestamp()
    if f"## {today}" in cl_content:
        insert_pos = cl_content.find(f"## {today}")
        section_end = cl_content.find("\n## ", insert_pos + 1)
        if section_end == -1:
            section_end = len(cl_content)
        cl_content = (
            cl_content[:section_end].rstrip()
            + f"\n- [{project}] {summary}\n"
            + cl_content[section_end:]
        )
    else:
        first_section = cl_content.find("\n## ")
        if first_section == -1:
            first_section = len(cl_content)
        cl_content = (
            cl_content[:first_section]
            + f"\n## {today}\n\n- [{project}] {summary}\n"
            + cl_content[first_section:]
        )

    changelog.write_text(cl_content, encoding="utf-8")

    # 3. Regenerate snapshot
    snapshot = get_dashboard()
    snapshot_path = PROJECTS_ROOT / "STATUS_SNAPSHOT.md"
    snapshot_path.write_text(snapshot, encoding="utf-8")

    return (
        f"Session closed for '{project}' at {_timestamp()}.\n"
        f"Updated: {project}/LOG.md, CHANGELOG.md, STATUS_SNAPSHOT.md"
    )


def main():
    transport = os.environ.get("MCP_TRANSPORT", "streamable-http")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
