"""Configuration management for the Ledger application."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, validator

# Load environment variables from .env file
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # MetaTrader 5 Configuration
    mt5_account_number: Optional[str] = None
    mt5_server: Optional[str] = None

    # Notion Configuration
    notion_api_key: Optional[str] = None
    notion_database_id: Optional[str] = None

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
