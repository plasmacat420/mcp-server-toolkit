"""System information tool using psutil and the platform module."""

import platform
import socket
import time

import psutil


async def get_system_info() -> dict:
    """Return a snapshot of the host system's resource usage and identity.

    Returns:
        Dict with keys ``os``, ``os_version``, ``python_version``,
        ``cpu_count``, ``memory_gb``, ``memory_used_pct``,
        ``disk_free_gb``, ``hostname``, and ``uptime_hours``, or
        ``{"error": message}`` on failure.
    """
    try:
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        uptime_seconds = time.time() - psutil.boot_time()

        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(logical=True),
            "memory_gb": round(mem.total / (1024**3), 2),
            "memory_used_pct": round(mem.percent, 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "hostname": socket.gethostname(),
            "uptime_hours": round(uptime_seconds / 3600, 2),
        }
    except Exception as exc:
        return {"error": str(exc)}
