"""Tests for database tools: query_sqlite and list_tables."""

import aiosqlite
import pytest

from mcp_toolkit.tools.database import list_tables, query_sqlite


@pytest.fixture()
async def db_path(tmp_path):
    """Create a temporary SQLite database seeded with test data."""
    db_file = tmp_path / "test.db"
    async with aiosqlite.connect(str(db_file)) as db:
        await db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        await db.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT)")
        await db.execute("INSERT INTO users VALUES (1, 'Alice'), (2, 'Bob')")
        await db.commit()
    return str(db_file)


async def test_list_tables(db_path):
    """list_tables returns all table names."""
    result = await list_tables(db_path)

    assert "error" not in result
    assert result["count"] == 2
    assert "users" in result["tables"]
    assert "products" in result["tables"]


async def test_query_sqlite_select(db_path):
    """query_sqlite returns correct columns and rows for a SELECT."""
    result = await query_sqlite(db_path, "SELECT * FROM users ORDER BY id")

    assert "error" not in result
    assert result["columns"] == ["id", "name"]
    assert result["row_count"] == 2
    assert result["rows"][0] == [1, "Alice"]
    assert result["rows"][1] == [2, "Bob"]


async def test_query_sqlite_rejects_insert(db_path):
    """query_sqlite refuses INSERT statements."""
    result = await query_sqlite(db_path, "INSERT INTO users VALUES (3, 'Charlie')")

    assert "error" in result
    assert "SELECT" in result["error"]


async def test_query_sqlite_rejects_drop(db_path):
    """query_sqlite refuses DROP statements."""
    result = await query_sqlite(db_path, "DROP TABLE users")

    assert "error" in result


async def test_query_sqlite_bad_path():
    """query_sqlite returns an error for a nonexistent database file."""
    result = await query_sqlite("/nonexistent/path/db.sqlite", "SELECT 1")

    assert "error" in result
