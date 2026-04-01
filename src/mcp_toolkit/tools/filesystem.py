"""Filesystem tools: read files and search by glob pattern."""

from datetime import datetime, timezone
from pathlib import Path

from mcp_toolkit.config import settings


def _resolve_safe(path: str) -> tuple[Path, str | None]:
    """Resolve a path and verify it sits inside ROOT_DIR.

    Args:
        path: Absolute or relative path string supplied by the caller.

    Returns:
        A tuple of (resolved_path, error_message). error_message is None
        when the path is safe.
    """
    root = settings.ROOT_DIR.resolve()
    target = Path(path)
    if not target.is_absolute():
        target = (root / target).resolve()
    else:
        target = target.resolve()

    try:
        target.relative_to(root)
    except ValueError:
        return target, f"Access denied: path '{path}' is outside ROOT_DIR"

    return target, None


async def read_file(path: str) -> dict:
    """Read a text file and return its content with line numbers.

    Args:
        path: Path to the file. Relative paths are resolved against ROOT_DIR.

    Returns:
        Dict with keys ``content``, ``path``, ``lines``, ``size_bytes``, or
        ``{"error": message}`` on failure.
    """
    try:
        target, err = _resolve_safe(path)
        if err:
            return {"error": err}

        if not target.exists():
            return {"error": f"File not found: {path}"}
        if not target.is_file():
            return {"error": f"Not a file: {path}"}

        size_bytes = target.stat().st_size
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if size_bytes > max_bytes:
            return {
                "error": (f"File too large: {size_bytes} bytes (max {max_bytes} bytes)")
            }

        raw = target.read_text(encoding="utf-8", errors="replace")
        lines = raw.splitlines()
        numbered = "\n".join(f"{i + 1:4d} | {line}" for i, line in enumerate(lines))

        return {
            "content": numbered,
            "path": str(target),
            "lines": len(lines),
            "size_bytes": size_bytes,
        }
    except Exception as exc:
        return {"error": str(exc)}


async def search_files(directory: str, pattern: str, recursive: bool = True) -> dict:
    """Search for files matching a glob pattern inside a directory.

    Args:
        directory: Directory to search. Relative paths are resolved against
            ROOT_DIR.
        pattern: Glob pattern (e.g. ``"*.py"``).
        recursive: When True uses ``rglob``; otherwise uses ``glob``.

    Returns:
        Dict with keys ``results`` (list of {path, size, modified}) and
        ``count``, or ``{"error": message}`` on failure.
    """
    try:
        dir_path, err = _resolve_safe(directory)
        if err:
            return {"error": err}

        if not dir_path.exists():
            return {"error": f"Directory not found: {directory}"}
        if not dir_path.is_dir():
            return {"error": f"Not a directory: {directory}"}

        glob_fn = dir_path.rglob if recursive else dir_path.glob
        results = []
        for match in sorted(glob_fn(pattern)):
            if not match.is_file():
                continue
            stat = match.stat()
            results.append(
                {
                    "path": str(match),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                }
            )

        return {"results": results, "count": len(results)}
    except Exception as exc:
        return {"error": str(exc)}
