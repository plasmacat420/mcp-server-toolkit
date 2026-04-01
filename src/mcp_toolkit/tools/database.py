"""SQLite database tools: execute SELECT queries and list tables."""

import aiosqlite


async def query_sqlite(db_path: str, sql: str) -> dict:
    """Execute a SELECT query against a SQLite database file.

    Only SELECT statements are permitted; any other statement type returns
    an error without touching the database.

    Args:
        db_path: Path to the SQLite database file.
        sql: SQL SELECT statement to execute.

    Returns:
        Dict with keys ``columns``, ``rows``, and ``row_count``, or
        ``{"error": message}`` on failure.
    """
    try:
        stripped = sql.strip()
        first_token = stripped.split()[0].upper() if stripped else ""
        if first_token != "SELECT":
            return {"error": (f"Only SELECT queries are allowed, got: {first_token}")}

        async with aiosqlite.connect(db_path) as db:
            async with db.execute(sql) as cursor:
                rows = await cursor.fetchall()
                columns = (
                    [col_desc[0] for col_desc in cursor.description]
                    if cursor.description
                    else []
                )
                return {
                    "columns": columns,
                    "rows": [list(row) for row in rows],
                    "row_count": len(rows),
                }
    except Exception as exc:
        return {"error": str(exc)}


async def list_tables(db_path: str) -> dict:
    """List all user-defined tables in a SQLite database.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        Dict with keys ``tables`` (sorted list of table names) and ``count``,
        or ``{"error": message}`` on failure.
    """
    try:
        async with aiosqlite.connect(db_path) as db:
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ) as cursor:
                rows = await cursor.fetchall()
                tables = [row[0] for row in rows]
                return {"tables": tables, "count": len(tables)}
    except Exception as exc:
        return {"error": str(exc)}
