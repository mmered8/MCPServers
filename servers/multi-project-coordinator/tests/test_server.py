"""Tests for Multi-Project Coordinator MCP server."""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

# Set up a test project root before importing server
_TEST_ROOT = None


@pytest.fixture(autouse=True)
def setup_test_root(tmp_path):
    """Create a temporary project structure for testing."""
    global _TEST_ROOT

    # Create project structure
    projects = tmp_path / "projects"
    projects.mkdir()

    # Project: test-project
    proj = projects / "test-project"
    proj.mkdir()
    (proj / "STATUS.md").write_text(
        "# Test Project Status\n\n- Health: GREEN\n- Overall progress: 75%\n- Blocker: None\n",
        encoding="utf-8",
    )
    (proj / "TASKS.md").write_text(
        "# Test Project Tasks\n\n## Active\n\n- [ ] Build feature A\n- [ ] Fix bug B\n\n## Completed\n\n- [x] Setup repo\n",
        encoding="utf-8",
    )
    (proj / "LOG.md").write_text(
        "# Test Project Log\n\n## 2026-03-20\n\nInitial setup complete.\n",
        encoding="utf-8",
    )
    (proj / "MEMORY.md").write_text(
        "# Test Project Memory\n\nKey decision: use FastAPI for the backend.\n",
        encoding="utf-8",
    )
    (proj / "PLAN.md").write_text(
        "# Test Project Plan\n\nBuild an MVP in 4 weeks.\n",
        encoding="utf-8",
    )

    # Project: another-project
    proj2 = projects / "another-project"
    proj2.mkdir()
    (proj2 / "STATUS.md").write_text(
        "# Another Project\n\n- Health: YELLOW\n- Progress: 30%\n- Blocker: waiting for API keys\n",
        encoding="utf-8",
    )
    (proj2 / "TASKS.md").write_text(
        "# Another Tasks\n\n## Active\n\n- [ ] Get API keys\n",
        encoding="utf-8",
    )
    (proj2 / "LOG.md").write_text("# Another Log\n", encoding="utf-8")

    # Template (should be ignored)
    template = projects / "_template"
    template.mkdir()
    (template / "STATUS.md").write_text("template", encoding="utf-8")

    # Ideation
    ideation = tmp_path / "ideation"
    ideation.mkdir()
    (ideation / "PIPELINE.md").write_text(
        "# Pipeline\n\n## BUILDING\n\n### Project A\n\n### Project B\n\n## READY TO BUILD\n\n### Project C\n\n## EVALUATING\n\n## RAW\n\n### Idea X\n### Idea Y\n### Idea Z\n",
        encoding="utf-8",
    )

    # Changelog
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 2026-03-20\n\n- Initial setup\n",
        encoding="utf-8",
    )

    # Patch the module paths
    os.environ["PROJECTS_ROOT"] = str(tmp_path)

    # Re-import to pick up env var
    import importlib
    import multi_project_coordinator.server as srv
    srv.PROJECTS_ROOT = tmp_path
    srv.PROJECTS_DIR = tmp_path / "projects"
    srv.IDEATION_DIR = tmp_path / "ideation"

    _TEST_ROOT = tmp_path
    yield tmp_path


def test_mcp_import():
    """Test that the FastMCP instance can be imported."""
    from multi_project_coordinator.server import mcp
    assert mcp is not None
    assert hasattr(mcp, "tool")


def test_get_dashboard(setup_test_root):
    from multi_project_coordinator.server import get_dashboard
    result = get_dashboard()
    assert "Another Project" in result
    assert "Test Project" in result
    assert "GREEN" in result
    assert "YELLOW" in result
    assert "75%" in result
    assert "PIPELINE" in result
    assert "BUILDING: 2" in result
    assert "RAW: 3" in result


def test_get_dashboard_no_side_effect(setup_test_root):
    """get_dashboard should NOT write a snapshot file."""
    from multi_project_coordinator.server import get_dashboard
    get_dashboard()
    assert not (setup_test_root / "STATUS_SNAPSHOT.md").exists()


def test_get_project_status(setup_test_root):
    from multi_project_coordinator.server import get_project_status
    result = get_project_status("test-project")
    assert "GREEN" in result
    assert "Build feature A" in result
    assert "Fix bug B" in result


def test_get_project_status_invalid(setup_test_root):
    from multi_project_coordinator.server import get_project_status
    with pytest.raises(ValueError, match="not found"):
        get_project_status("nonexistent")


def test_get_project_status_path_traversal(setup_test_root):
    """Path traversal attempts should be rejected."""
    from multi_project_coordinator.server import get_project_status
    with pytest.raises(ValueError, match="cannot contain"):
        get_project_status("../../etc")
    with pytest.raises(ValueError, match="cannot contain"):
        get_project_status("foo/bar")
    with pytest.raises(ValueError, match="cannot contain"):
        get_project_status("foo\\bar")


def test_get_pipeline(setup_test_root):
    from multi_project_coordinator.server import get_pipeline
    result = get_pipeline()
    assert "BUILDING" in result
    assert "Project A" in result
    assert "Idea X" in result


def test_append_log(setup_test_root):
    from multi_project_coordinator.server import append_log
    result = append_log("test-project", "Added new feature.")
    assert "Appended" in result

    log_content = (setup_test_root / "projects" / "test-project" / "LOG.md").read_text()
    assert "Added new feature." in log_content
    # Original content preserved
    assert "Initial setup complete." in log_content


def test_update_task_done(setup_test_root):
    from multi_project_coordinator.server import update_task
    result = update_task("test-project", "feature A", "done")
    assert "done" in result
    assert "line" in result  # Should include line number

    tasks = (setup_test_root / "projects" / "test-project" / "TASKS.md").read_text()
    assert "[x]" in tasks
    assert "completed" in tasks.lower()


def test_update_task_blocked(setup_test_root):
    from multi_project_coordinator.server import update_task
    result = update_task("test-project", "bug B", "blocked")
    assert "blocked" in result

    tasks = (setup_test_root / "projects" / "test-project" / "TASKS.md").read_text()
    assert "blocked" in tasks.lower()


def test_update_task_not_found(setup_test_root):
    from multi_project_coordinator.server import update_task
    result = update_task("test-project", "nonexistent task", "done")
    assert "not found" in result


def test_search_context(setup_test_root):
    from multi_project_coordinator.server import search_context
    result = search_context("FastAPI")
    assert "test-project/MEMORY.md" in result
    assert "FastAPI" in result


def test_search_context_searches_all_md(setup_test_root):
    """search_context should find matches in STATUS.md and TASKS.md too."""
    from multi_project_coordinator.server import search_context
    result = search_context("GREEN")
    assert "test-project/STATUS.md" in result

    result2 = search_context("feature A")
    assert "test-project/TASKS.md" in result2


def test_search_context_no_results(setup_test_root):
    from multi_project_coordinator.server import search_context
    result = search_context("xyznonexistent")
    assert "No matches" in result


def test_setup_project(setup_test_root):
    from multi_project_coordinator.server import setup_project
    result = setup_project("new-app")
    assert "Created project" in result

    project_dir = setup_test_root / "projects" / "new-app"
    assert project_dir.exists()
    assert (project_dir / "STATUS.md").exists()
    assert (project_dir / "TASKS.md").exists()
    assert (project_dir / "LOG.md").exists()
    assert (project_dir / "MEMORY.md").exists()
    assert (project_dir / "PLAN.md").exists()

    status = (project_dir / "STATUS.md").read_text()
    assert "New App" in status
    assert "GREY" in status


def test_setup_project_duplicate(setup_test_root):
    from multi_project_coordinator.server import setup_project
    with pytest.raises(ValueError, match="already exists"):
        setup_project("test-project")


def test_setup_project_invalid_name(setup_test_root):
    from multi_project_coordinator.server import setup_project
    with pytest.raises(ValueError):
        setup_project("../../bad")
    with pytest.raises(ValueError):
        setup_project("Bad Name")


def test_session_close(setup_test_root):
    from multi_project_coordinator.server import session_close
    result = session_close(
        "test-project",
        "Built the dashboard endpoint",
        "server.py, test_server.py",
        "Add authentication",
    )
    assert "Session closed" in result

    # Check LOG.md updated
    log = (setup_test_root / "projects" / "test-project" / "LOG.md").read_text()
    assert "Built the dashboard endpoint" in log

    # Check CHANGELOG.md updated
    changelog = (setup_test_root / "CHANGELOG.md").read_text()
    assert "test-project" in changelog
    assert "Built the dashboard endpoint" in changelog

    # Check snapshot generated (session_close writes it)
    snapshot = (setup_test_root / "STATUS_SNAPSHOT.md").read_text()
    assert "Test Project" in snapshot


def test_session_close_creates_missing_changelog(setup_test_root):
    """session_close should create CHANGELOG.md if it doesn't exist."""
    from multi_project_coordinator.server import session_close
    # Remove the existing changelog
    (setup_test_root / "CHANGELOG.md").unlink()

    result = session_close(
        "test-project", "First session", "files", "next steps"
    )
    assert "Session closed" in result
    changelog = (setup_test_root / "CHANGELOG.md").read_text()
    assert "First session" in changelog


def test_create_task_default_section(setup_test_root):
    """create_task should add a task under ## Active by default."""
    from multi_project_coordinator.server import create_task
    result = create_task("test-project", "Implement login page")
    assert "Added task" in result
    assert "Active" in result

    tasks = (setup_test_root / "projects" / "test-project" / "TASKS.md").read_text()
    assert "- [ ] Implement login page" in tasks
    assert "added" in tasks.lower()


def test_create_task_specific_section(setup_test_root):
    """create_task should add a task under a specified section."""
    from multi_project_coordinator.server import create_task

    # Add a Backlog section first
    tasks_file = setup_test_root / "projects" / "test-project" / "TASKS.md"
    content = tasks_file.read_text()
    tasks_file.write_text(content + "\n## Backlog\n\n", encoding="utf-8")

    result = create_task("test-project", "Research caching", "Backlog")
    assert "Added task" in result
    assert "Backlog" in result

    tasks = tasks_file.read_text()
    assert "Research caching" in tasks


def test_create_task_duplicate(setup_test_root):
    """create_task should reject duplicate tasks."""
    from multi_project_coordinator.server import create_task
    result = create_task("test-project", "Build feature A")
    assert "already exists" in result


def test_create_task_invalid_section(setup_test_root):
    """create_task should report available sections when target not found."""
    from multi_project_coordinator.server import create_task
    result = create_task("test-project", "Some task", "Nonexistent")
    assert "not found" in result
    assert "Active" in result  # Should list available sections


def test_create_task_creates_missing_tasks_file(setup_test_root):
    """create_task should create TASKS.md if it doesn't exist."""
    from multi_project_coordinator.server import create_task

    # Remove TASKS.md from another-project to test creation
    tasks_file = setup_test_root / "projects" / "another-project" / "TASKS.md"
    tasks_file.unlink()
    assert not tasks_file.exists()

    result = create_task("another-project", "Bootstrap project")
    assert "Added task" in result
    assert tasks_file.exists()

    content = tasks_file.read_text()
    assert "Bootstrap project" in content
    assert "## Active" in content


def test_get_git_status_with_repo(setup_test_root):
    """get_git_status should report branch, changes, and last commit for a git repo."""
    from multi_project_coordinator.server import get_git_status

    # Initialize a git repo in the test project directory
    proj_dir = setup_test_root / "projects" / "test-project"
    subprocess.run(["git", "init"], cwd=proj_dir, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=proj_dir, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=proj_dir, capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=proj_dir, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=proj_dir, capture_output=True,
    )

    result = get_git_status("test-project")
    assert "test-project" in result
    assert "Branch:" in result
    assert "Uncommitted changes: 0" in result
    assert "Last commit:" in result
    assert "(no commits)" not in result


def test_get_git_status_no_repo(setup_test_root, tmp_path):
    """get_git_status should handle directories that are not git repos."""
    from multi_project_coordinator.server import get_git_status
    import multi_project_coordinator.server as srv

    # Create an isolated project outside any git repo
    isolated = tmp_path / "isolated"
    isolated.mkdir()
    projects = isolated / "projects"
    projects.mkdir()
    proj = projects / "no-git"
    proj.mkdir()
    (proj / "STATUS.md").write_text("# No Git\n- Health: GREY\n", encoding="utf-8")

    srv.PROJECTS_ROOT = isolated
    srv.PROJECTS_DIR = projects
    srv.IDEATION_DIR = isolated / "ideation"

    result = get_git_status("no-git")
    assert "not inside a git repository" in result
