"""MCP Server Toolkit — main server entry point."""

import sys

from fastmcp import FastMCP
from loguru import logger

from mcp_toolkit.config import settings
from mcp_toolkit.tools.database import list_tables, query_sqlite
from mcp_toolkit.tools.filesystem import read_file, search_files
from mcp_toolkit.tools.system import get_system_info
from mcp_toolkit.tools.websearch import web_search

# Configure loguru
logger.remove()
logger.add(sys.stderr, level=settings.LOG_LEVEL)

mcp = FastMCP("MCP Server Toolkit")

# Register all tools
mcp.tool()(read_file)
mcp.tool()(search_files)
mcp.tool()(web_search)
mcp.tool()(query_sqlite)
mcp.tool()(list_tables)
mcp.tool()(get_system_info)


def main() -> None:
    """Entry point for the MCP server.

    Selects transport (stdio or SSE) based on the TRANSPORT environment
    variable, then starts the server.
    """
    logger.info("Starting MCP Server Toolkit (transport={})", settings.TRANSPORT)
    if settings.TRANSPORT == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=8000)
    else:
        mcp.run(transport="stdio")
