# MCP Server Toolkit

> A production-ready MCP server exposing filesystem, web search, SQLite, and system tools —
> plug directly into Claude Desktop or any MCP-compatible client.

![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CI](https://github.com/plasmacat420/mcp-server-toolkit/actions/workflows/ci.yml/badge.svg)
![Docker](https://img.shields.io/badge/docker-ghcr.io-blue?logo=docker)

---

## What is MCP?

The **Model Context Protocol** is an open standard that lets AI assistants like Claude
securely call external tools — giving them real-time access to your filesystem, databases,
and the web without you having to paste content into the chat manually.

---

## Features

- **Filesystem** — `read_file` returns any text file with numbered lines; `search_files`
  globs a directory tree. Both tools enforce a configurable `ROOT_DIR` so path-traversal
  attacks are impossible.
- **Web Search** — `web_search` queries DuckDuckGo's free JSON API. No API key, no rate
  limits, async with a 10 s timeout.
- **SQLite** — `query_sqlite` runs SELECT-only queries and returns typed columns + rows;
  `list_tables` shows the schema at a glance.
- **System** — `get_system_info` snapshots OS, Python version, CPU count, memory usage,
  free disk, hostname, and uptime in one call.

---

## Quick Start

**Option 1 — pip**

```bash
pip install git+https://github.com/plasmacat420/mcp-server-toolkit.git
mcp-toolkit          # starts the server on stdio (Claude Desktop mode)
```

**Option 2 — Docker**

```bash
docker pull ghcr.io/plasmacat420/mcp-server-toolkit:latest
docker run -it ghcr.io/plasmacat420/mcp-server-toolkit:latest
```

**Option 3 — Docker Compose (recommended for SSE / networked use)**

```bash
git clone https://github.com/plasmacat420/mcp-server-toolkit
cd mcp-server-toolkit
cp .env.example .env          # edit ROOT_DIR if needed
docker compose up
```

The SSE endpoint is then available at `http://localhost:8000`.

---

## Claude Desktop Integration

Add the following block to `claude_desktop_config.json`
(`~/Library/Application Support/Claude/` on macOS,
`%APPDATA%\Claude\` on Windows):

```json
{
  "mcpServers": {
    "mcp-toolkit": {
      "command": "mcp-toolkit",
      "env": {
        "ROOT_DIR": "/Users/you/projects"
      }
    }
  }
}
```

Restart Claude Desktop — the four tool categories appear automatically in every conversation.

---

## Tool Reference

| Tool | Description | Parameters | Returns |
|---|---|---|---|
| `read_file` | Read a text file with line numbers | `path: str` | `{content, path, lines, size_bytes}` |
| `search_files` | Glob-search inside a directory | `directory: str`, `pattern: str`, `recursive: bool = True` | `{results[], count}` |
| `web_search` | DuckDuckGo search (no key needed) | `query: str`, `max_results: int = 5` | `{results[], query, count}` |
| `query_sqlite` | Execute a SELECT query | `db_path: str`, `sql: str` | `{columns[], rows[], row_count}` |
| `list_tables` | List all tables in a SQLite DB | `db_path: str` | `{tables[], count}` |
| `get_system_info` | Host OS / resource snapshot | _(none)_ | `{os, cpu_count, memory_gb, …}` |

---

## CLI Usage

The `mcp-client` binary lets you call any tool from your terminal:

```bash
# Search for Python files
mcp-client search-files . "*.py"
# {"results": [...], "count": 12}

# Read a file
mcp-client read-file src/mcp_toolkit/server.py
# {"content": "   1 | \"\"\"MCP Server Toolkit...", "lines": 34, ...}

# Web search
mcp-client web-search "python asyncio tutorial" --max-results 3
# {"results": [{"title": "...", "url": "...", "snippet": "..."}], ...}

# Query a SQLite database
mcp-client query-db examples/sample.db "SELECT name, email FROM users LIMIT 3"
# {"columns": ["name", "email"], "rows": [["Alice Johnson", "alice@..."]], ...}

# System snapshot
mcp-client system-info
# {"os": "Linux", "cpu_count": 8, "memory_gb": 15.87, ...}

# Full demo against sample.db
mcp-client demo
```

---

## Development

```bash
git clone https://github.com/plasmacat420/mcp-server-toolkit
cd mcp-server-toolkit

# Install with dev extras
pip install -e ".[dev]"

# Create the sample database
python examples/create_db.py

# Run the test suite
pytest -v

# Lint + format check
ruff check .
ruff format --check .

# Auto-fix
ruff check . --fix && ruff format .

# Full demo (requires sample.db)
python examples/demo.py
```

### Running a single test

```bash
pytest tests/test_filesystem.py::test_read_file_success -v
```

---

## Architecture

The server is built on **FastMCP**, which handles the MCP wire protocol.
Each tool category lives in its own module under `src/mcp_toolkit/tools/`;
the modules export plain `async` functions that know nothing about MCP.
`server.py` creates the `FastMCP` instance, imports every tool function,
and registers them with `mcp.tool()`. Configuration is a single
`pydantic-settings` `BaseSettings` object (`config.py`) that reads from
environment variables or a `.env` file. The CLI client (`client/cli.py`)
imports the same async functions directly — no MCP protocol involved —
making it easy to smoke-test individual tools.

```
src/mcp_toolkit/
├── server.py        ← FastMCP app + tool registration
├── config.py        ← pydantic-settings Settings singleton
└── tools/
    ├── filesystem.py   read_file, search_files
    ├── websearch.py    web_search
    ├── database.py     query_sqlite, list_tables
    └── system.py       get_system_info
```

---

## License

MIT © plasmacat420
