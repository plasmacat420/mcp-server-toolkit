# MCP Server Toolkit

> A production-ready MCP server exposing filesystem, web search, SQLite, and system tools —
> plug directly into Claude Desktop or any MCP-compatible client.

[View on GitHub](https://github.com/plasmacat420/mcp-server-toolkit){ .md-button }

---

## What is MCP?

The **Model Context Protocol** is an open standard that lets AI assistants like Claude
securely call external tools — giving them controlled access to your filesystem, databases,
and the web without you having to paste content manually.

---

## Features

| Category | Tools | Description |
|---|---|---|
| **Filesystem** | `read_file`, `search_files` | Read text files with line numbers; glob search with path-traversal protection |
| **Web Search** | `web_search` | DuckDuckGo search — no API key needed |
| **Database** | `query_sqlite`, `list_tables` | Run SELECT queries on SQLite files; SELECT-only enforcement |
| **System** | `get_system_info` | OS, CPU, memory, disk, and uptime snapshot |

---

## Installation

=== "pip"

    ```bash
    pip install git+https://github.com/plasmacat420/mcp-server-toolkit.git
    mcp-toolkit
    ```

=== "Docker"

    ```bash
    docker pull ghcr.io/plasmacat420/mcp-server-toolkit:latest
    docker run -it ghcr.io/plasmacat420/mcp-server-toolkit:latest
    ```

=== "Docker Compose"

    ```bash
    git clone https://github.com/plasmacat420/mcp-server-toolkit
    cd mcp-server-toolkit
    cp .env.example .env
    docker compose up
    ```

---

## Claude Desktop Integration

Add the following to your `claude_desktop_config.json`:

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

---

## Tool Reference

| Tool | Description | Key Parameters | Returns |
|---|---|---|---|
| `read_file` | Read a text file with line numbers | `path: str` | `{content, path, lines, size_bytes}` |
| `search_files` | Glob-search a directory | `directory, pattern, recursive` | `{results[], count}` |
| `web_search` | DuckDuckGo web search | `query, max_results` | `{results[], query, count}` |
| `query_sqlite` | Execute a SELECT query | `db_path, sql` | `{columns[], rows[], row_count}` |
| `list_tables` | List tables in a SQLite DB | `db_path` | `{tables[], count}` |
| `get_system_info` | Host system snapshot | _(none)_ | `{os, cpu_count, memory_gb, …}` |

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `ROOT_DIR` | `./` | Filesystem tools are locked to this directory |
| `TRANSPORT` | `stdio` | `stdio` for Claude Desktop, `sse` for Docker/network |
| `LOG_LEVEL` | `INFO` | Loguru log level |
| `MAX_FILE_SIZE_MB` | `10` | Maximum file size readable by `read_file` |

---

*Built with [FastMCP](https://github.com/jlowin/fastmcp) · Licensed MIT*
