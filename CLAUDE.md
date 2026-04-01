# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An MCP (Model Context Protocol) server built with FastMCP that exposes four tool categories: filesystem read/search, DuckDuckGo web search, SQLite querying, and system info. Includes a Click CLI client, Docker support, and GitHub Actions CI.

## Common Commands

```bash
# Install in dev mode (from repo root)
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_filesystem.py -v

# Run a single test by name
pytest tests/test_filesystem.py::test_read_file -v

# Run tests with coverage
pytest --cov=src/mcp_toolkit --cov-report=term-missing

# Lint
ruff check .

# Format check
ruff format --check .

# Auto-fix lint issues
ruff check . --fix && ruff format .

# Start the server (stdio transport, default)
mcp-toolkit

# Start the server (SSE transport)
TRANSPORT=sse mcp-toolkit

# CLI client commands
mcp-client search-files --directory . --pattern "*.py"
mcp-client read-file --path src/mcp_toolkit/server.py
mcp-client web-search --query "python asyncio"
mcp-client query-db --db examples/sample.db --sql "SELECT * FROM users"
mcp-client system-info
mcp-client --demo   # runs all tools against sample.db

# Create the sample database
python examples/create_db.py

# Run the full demo
python examples/demo.py

# Docker
docker-compose up --build
docker build -t mcp-toolkit .
```

## Architecture

### Server Entry Point (`src/mcp_toolkit/server.py`)
FastMCP server that imports and registers all tools from the `tools/` submodules. Transport mode (stdio vs SSE) is selected at startup via the `TRANSPORT` env var. `main()` is the script entry point.

### Tools Pattern (`src/mcp_toolkit/tools/`)
Each module defines async tool functions decorated with `@mcp.tool()` (or equivalent FastMCP registration). Every tool returns either its data payload or `{"error": "message"}` on failure — never raises to the caller. Tools are imported and registered in `server.py`.

- **filesystem.py**: `read_file`, `search_files` — path traversal is blocked; all paths must resolve under `ROOT_DIR` from config
- **websearch.py**: `web_search` — uses DuckDuckGo's free API via `httpx` async client; mock `httpx` in tests, never hit real network
- **database.py**: `query_sqlite`, `list_tables` — only SELECT queries allowed; uses `aiosqlite`
- **system.py**: `get_system_info` — uses `psutil` for memory/disk stats

### Configuration (`src/mcp_toolkit/config.py`)
`pydantic-settings` `BaseSettings` class loaded once at import. Key fields: `ROOT_DIR`, `TRANSPORT`, `LOG_LEVEL`, `MAX_FILE_SIZE_MB`. Tests that need different config values should monkeypatch the settings object.

### CLI Client (`client/cli.py`)
Click group that imports tool functions directly (not via MCP protocol) and pretty-prints output with `rich`. Entry point: `mcp-client`.

## Key Constraints

- All tool functions must be `async` — no blocking I/O
- `read_file` and `search_files` must reject paths outside `ROOT_DIR` (path traversal guard)
- `query_sqlite` must reject any SQL that isn't a SELECT statement
- `web_search` has a 10s httpx timeout
- Max file size for `read_file` is enforced from `MAX_FILE_SIZE_MB` config

## Testing Notes

- `asyncio_mode = "auto"` is set in `pyproject.toml` — no need for `@pytest.mark.asyncio`
- Filesystem tests use `tmp_path` pytest fixture for isolated temp dirs
- Web search tests use `respx` to mock `httpx.AsyncClient` — never make real HTTP calls; add `@respx.mock` decorator to each test
- Database tests create an in-memory or tmp SQLite file per test

## Transport Modes

- **stdio** (default): server communicates over stdin/stdout — used when Claude Desktop or another MCP host spawns the process
- **SSE**: server listens on port 8000 — used in Docker/networked deployments; set `TRANSPORT=sse`

## Claude Desktop Integration

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-toolkit": {
      "command": "mcp-toolkit",
      "env": {
        "ROOT_DIR": "/path/to/allowed/directory"
      }
    }
  }
}
```
