"""Tests for filesystem tools: read_file and search_files."""

import pytest

from mcp_toolkit.config import settings
from mcp_toolkit.tools.filesystem import read_file, search_files


@pytest.fixture()
def tmp_root(tmp_path, monkeypatch):
    """Set ROOT_DIR to an isolated temp directory for the duration of the test."""
    monkeypatch.setattr(settings, "ROOT_DIR", tmp_path)
    return tmp_path


async def test_read_file_success(tmp_root):
    """read_file returns numbered content for a valid file inside ROOT_DIR."""
    test_file = tmp_root / "hello.txt"
    test_file.write_text("line one\nline two\nline three")

    result = await read_file("hello.txt")

    assert "error" not in result
    assert result["lines"] == 3
    assert result["size_bytes"] > 0
    assert "   1 | line one" in result["content"]
    assert "   3 | line three" in result["content"]


async def test_read_file_path_traversal(tmp_root):
    """read_file rejects paths that escape ROOT_DIR."""
    result = await read_file("../../../etc/passwd")

    assert "error" in result
    assert "outside ROOT_DIR" in result["error"]


async def test_read_file_not_found(tmp_root):
    """read_file returns an error for a missing file."""
    result = await read_file("nonexistent.txt")

    assert "error" in result


async def test_read_file_too_large(tmp_root, monkeypatch):
    """read_file rejects files that exceed MAX_FILE_SIZE_MB."""
    monkeypatch.setattr(settings, "MAX_FILE_SIZE_MB", 0)
    big_file = tmp_root / "big.txt"
    big_file.write_text("x" * 1024)

    result = await read_file("big.txt")

    assert "error" in result
    assert "too large" in result["error"]


async def test_search_files(tmp_root):
    """search_files finds all files matching the pattern."""
    for i in range(3):
        (tmp_root / f"script_{i}.py").write_text(f"# script {i}")
    (tmp_root / "readme.txt").write_text("not python")

    result = await search_files(str(tmp_root), "*.py")

    assert "error" not in result
    assert result["count"] == 3
    assert all(r["path"].endswith(".py") for r in result["results"])


async def test_search_files_path_traversal(tmp_root):
    """search_files rejects a directory outside ROOT_DIR."""
    result = await search_files("../../", "*.py")

    assert "error" in result
    assert "outside ROOT_DIR" in result["error"]
