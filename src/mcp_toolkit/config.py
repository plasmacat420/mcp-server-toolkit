"""Application settings loaded from environment variables or a .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the MCP toolkit server.

    All fields can be overridden via environment variables or a .env file.
    """

    ROOT_DIR: Path = Path("./")
    TRANSPORT: str = "stdio"
    LOG_LEVEL: str = "INFO"
    MAX_FILE_SIZE_MB: int = 10

    model_config = {"env_file": ".env"}


settings = Settings()
