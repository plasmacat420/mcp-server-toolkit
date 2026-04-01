"""Click CLI client — calls MCP tool functions directly and pretty-prints output."""

import asyncio
import json

import click
from rich import print_json
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.group()
def cli() -> None:
    """MCP Server Toolkit CLI — call any tool from the terminal."""


@cli.command("read-file")
@click.argument("path")
def cmd_read_file(path: str) -> None:
    """Read a file and display its content with line numbers.

    Args:
        path: Path to the file to read.
    """
    from mcp_toolkit.tools.filesystem import read_file

    result = asyncio.run(read_file(path))
    print_json(json.dumps(result))


@cli.command("search-files")
@click.argument("directory")
@click.argument("pattern")
@click.option(
    "--no-recursive",
    is_flag=True,
    default=False,
    help="Disable recursive search.",
)
def cmd_search_files(directory: str, pattern: str, no_recursive: bool) -> None:
    """Search for files matching PATTERN inside DIRECTORY.

    Args:
        directory: Root directory to search.
        pattern: Glob pattern (e.g. '*.py').
        no_recursive: When set, only searches the top-level directory.
    """
    from mcp_toolkit.tools.filesystem import search_files

    result = asyncio.run(search_files(directory, pattern, recursive=not no_recursive))
    print_json(json.dumps(result))


@cli.command("web-search")
@click.argument("query")
@click.option(
    "--max-results",
    default=5,
    show_default=True,
    help="Maximum number of results to return.",
)
def cmd_web_search(query: str, max_results: int) -> None:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string.
        max_results: Maximum number of results.
    """
    from mcp_toolkit.tools.websearch import web_search

    result = asyncio.run(web_search(query, max_results=max_results))
    print_json(json.dumps(result))


@cli.command("query-db")
@click.argument("db_path")
@click.argument("sql")
def cmd_query_db(db_path: str, sql: str) -> None:
    """Execute a SELECT query against a SQLite database.

    Args:
        db_path: Path to the SQLite .db file.
        sql: SELECT SQL statement to run.
    """
    from mcp_toolkit.tools.database import query_sqlite

    result = asyncio.run(query_sqlite(db_path, sql))
    print_json(json.dumps(result))


@cli.command("list-tables")
@click.argument("db_path")
def cmd_list_tables(db_path: str) -> None:
    """List all tables in a SQLite database.

    Args:
        db_path: Path to the SQLite .db file.
    """
    from mcp_toolkit.tools.database import list_tables

    result = asyncio.run(list_tables(db_path))
    print_json(json.dumps(result))


@cli.command("system-info")
def cmd_system_info() -> None:
    """Display current system information (OS, CPU, memory, disk)."""
    from mcp_toolkit.tools.system import get_system_info

    result = asyncio.run(get_system_info())
    print_json(json.dumps(result))


@cli.command("demo")
def cmd_demo() -> None:
    """Run all tools in sequence against examples/sample.db."""
    from mcp_toolkit.tools.database import list_tables, query_sqlite
    from mcp_toolkit.tools.filesystem import read_file, search_files
    from mcp_toolkit.tools.system import get_system_info
    from mcp_toolkit.tools.websearch import web_search

    async def _run() -> None:
        console.print(Panel("[bold green]MCP Server Toolkit — Demo[/bold green]"))

        console.print("\n[bold cyan]System Info[/bold cyan]")
        print_json(json.dumps(await get_system_info()))

        console.print("\n[bold cyan]Search Python Files[/bold cyan]")
        print_json(json.dumps(await search_files("src", "*.py", recursive=True)))

        console.print("\n[bold cyan]Read README[/bold cyan]")
        r = await read_file("README.md")
        if "error" not in r:
            r["content"] = r["content"][:300] + "\n... (truncated)"
        print_json(json.dumps(r))

        console.print("\n[bold cyan]List DB Tables[/bold cyan]")
        print_json(json.dumps(await list_tables("examples/sample.db")))

        console.print("\n[bold cyan]Query Users[/bold cyan]")
        print_json(
            json.dumps(
                await query_sqlite(
                    "examples/sample.db",
                    "SELECT name, email FROM users LIMIT 5",
                )
            )
        )

        console.print("\n[bold cyan]Web Search[/bold cyan]")
        print_json(
            json.dumps(await web_search("Model Context Protocol MCP", max_results=3))
        )

        console.print("\n[bold green]Demo complete.[/bold green]")

    asyncio.run(_run())
