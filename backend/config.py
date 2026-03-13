"""Application configuration settings."""
import platform
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


def get_app_data_dir() -> Path:
    """Get the platform-specific application data directory.

    Returns:
        macOS:   ~/Library/Application Support/Owork/
        Windows: %LOCALAPPDATA%/Owork/  (typically C:/Users/<user>/AppData/Local/Owork/)
        Linux:   ~/.local/share/owork/
    """
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Owork"
    elif system == "Windows":
        return Path.home() / "AppData" / "Local" / "Owork"
    else:
        return Path.home() / ".local" / "share" / "owork"

# Model mapping: display name -> (Anthropic API model ID, AWS Bedrock model ID)
MODEL_MAP: dict[str, tuple[str, str]] = {
    "Fast Model": ("claude-sonnet-4-6", "global.anthropic.claude-sonnet-4-6"),
    "Strong Model": ("claude-opus-4-6", "global.anthropic.claude-opus-4-6-v1"),
}

# Keys used as available model list in settings
ANTHROPIC_TO_BEDROCK_MODEL_MAP = MODEL_MAP


def resolve_model_id(display_name: str, use_bedrock: bool = False) -> str:
    """Resolve a display name to the actual model ID for the SDK.

    Args:
        display_name: The display name (e.g. "Fast Model") or raw model ID
        use_bedrock: If True, return the Bedrock model ID; otherwise the Anthropic API ID

    Returns:
        The resolved model ID, or the original string if no mapping exists
    """
    entry = MODEL_MAP.get(display_name)
    if entry:
        return entry[1] if use_bedrock else entry[0]
    return display_name


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Agent Platform API"
    app_version: str = "4.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS - include Tauri origins for desktop app
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:1420", "tauri://localhost", "https://tauri.localhost", "http://tauri.localhost"]

    # Database
    database_type: str = "sqlite"

    # SQLite configuration
    sqlite_db_path: str | None = None  # If None, uses default user data directory

    # AWS (for Bedrock model access)
    aws_region: str = "us-west-2"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_per_minute: int = 100

    # Claude Agent SDK / Anthropic API Configuration
    anthropic_api_key: str = ""
    anthropic_base_url: str | None = None  # Custom API endpoint (optional)
    default_model: str = "Fast Model"

    # Claude Code Configuration
    claude_code_use_bedrock: bool = True  # Use AWS Bedrock instead of Anthropic API
    claude_code_disable_experimental_betas: bool = True  # Disable experimental features

    # Agent workspace directory - main skills storage in .claude/skills/
    agent_workspace_dir: str = str(get_app_data_dir() / "workspace")

    # Isolated per-agent workspaces directory (OUTSIDE project tree for skill isolation)
    # Each agent gets its own workspace with absolute symlinks to allowed skills
    # This prevents agents from discovering skills in parent directories
    agent_workspaces_dir: str = str(get_app_data_dir() / "workspaces")

    # Built-in Sandbox Configuration (Claude Agent SDK native bash sandboxing)
    sandbox_enabled_default: bool = False  # Default sandbox state for new agents
    sandbox_auto_allow_bash: bool = True  # Auto-approve bash when sandboxed
    sandbox_excluded_commands: str = "docker"  # Comma-separated commands to bypass sandbox (e.g., "git,docker")
    sandbox_allow_unsandboxed: bool = False  # Allow model to bypass sandbox

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
