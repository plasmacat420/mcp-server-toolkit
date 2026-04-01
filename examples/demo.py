"""End-to-end smoke test: calls every tool and prints results with rich."""

import asyncio
import json
from pathlib import Path

from rich import print_json
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()
DB = str(Path(__file__).parent / "sample.db")


async def run_demo() -> None:
    """Exercise all six MCP tools and display their output."""
    # Import here so the demo also works when run before `pip install -e .`
    # as long as src/ is on PYTHONPATH.
    from mcp_toolkit.tools.database import list_tables, query_sqlite
    from mcp_toolkit.tools.filesystem import read_file, search_files
    from mcp_toolkit.tools.system import get_system_info
    from mcp_toolkit.tools.websearch import web_search

    console.print(
        Panel(
            "[bold green]MCP Server Toolkit — End-to-End Demo[/bold green]",
            subtitle="All six tools",
        )
    )

    # ── 1. System info ────────────────────────────────────────────────────
    console.print(Rule("[cyan]1 · get_system_info[/cyan]"))
    print_json(json.dumps(await get_system_info()))

    # ── 2. Search files ───────────────────────────────────────────────────
    console.print(Rule("[cyan]2 · search_files — *.py under src/[/cyan]"))
    print_json(json.dumps(await search_files("src", "*.py", recursive=True)))

    # ── 3. Read file ──────────────────────────────────────────────────────
    console.print(Rule("[cyan]3 · read_file — README.md (first 200 chars)[/cyan]"))
    r = await read_file("README.md")
    if "error" not in r:
        r = {**r, "content": r["content"][:200] + "\n…"}
    print_json(json.dumps(r))

    # ── 4. List tables ────────────────────────────────────────────────────
    console.print(Rule("[cyan]4 · list_tables — sample.db[/cyan]"))
    print_json(json.dumps(await list_tables(DB)))

    # ── 5. Query with JOIN ────────────────────────────────────────────────
    console.print(Rule("[cyan]5 · query_sqlite — orders JOIN users + products[/cyan]"))
    sql = (
        "SELECT u.name, p.name AS product, o.quantity, o.total "
        "FROM orders o "
        "JOIN users    u ON o.user_id    = u.id "
        "JOIN products p ON o.product_id = p.id "
        "LIMIT 5"
    )
    print_json(json.dumps(await query_sqlite(DB, sql)))

    # ── 6. Web search ─────────────────────────────────────────────────────
    console.print(Rule("[cyan]6 · web_search — 'Model Context Protocol'[/cyan]"))
    print_json(
        json.dumps(await web_search("Model Context Protocol MCP", max_results=3))
    )

    console.print(Panel("[bold green]All tools exercised successfully.[/bold green]"))


if __name__ == "__main__":
    asyncio.run(run_demo())
