"""Tests for the system info tool."""

from mcp_toolkit.tools.system import get_system_info

_EXPECTED_KEYS = {
    "os",
    "os_version",
    "python_version",
    "cpu_count",
    "memory_gb",
    "memory_used_pct",
    "disk_free_gb",
    "hostname",
    "uptime_hours",
}


async def test_get_system_info_keys():
    """get_system_info returns all expected keys without error."""
    result = await get_system_info()

    assert "error" not in result
    assert _EXPECTED_KEYS.issubset(result.keys())


async def test_memory_is_positive_float():
    """memory_gb is a positive float."""
    result = await get_system_info()

    assert isinstance(result["memory_gb"], float)
    assert result["memory_gb"] > 0.0


async def test_cpu_count_is_positive_int():
    """cpu_count is a positive integer."""
    result = await get_system_info()

    assert isinstance(result["cpu_count"], int)
    assert result["cpu_count"] >= 1


async def test_uptime_is_non_negative():
    """uptime_hours is a non-negative float."""
    result = await get_system_info()

    assert isinstance(result["uptime_hours"], float)
    assert result["uptime_hours"] >= 0.0
