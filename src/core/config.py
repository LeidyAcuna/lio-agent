import os

from src.core.exceptions import ConfigurationError


class Settings:
    """
    Configuration settings for the application.

    This class loads environment variables required for database connection,
    Telegram bot integration, and concurrency management.
    """

    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PW: str = os.getenv("POSTGRES_PW")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    TELEGRAM_BOT_TOKEN: str = os.getenv("TOKEN_TELEGRAM_LIO")
    MAX_CONCURRENCY_QUEUE: int = int(os.getenv("MAX_CONCURRENCY", "1"))
    OLLAMA_URL: str = os.getenv("OLLAMA_URL")

    _ids_str = os.getenv("ALLOWED_TELEGRAM_USER_IDS", "")
    ALLOWED_TELEGRAM_USER_IDS: list[int] = [
        int(uid.strip()) for uid in _ids_str.split(",") if uid.strip()
    ]


_settings = Settings()


def get_settings() -> Settings:
    return _settings


def validate_settings() -> None:
    """
    Validates and returns the application settings.

    This function ensures that all required environment variables are present.
    If any critical setting is missing, it raises a ConfigurationError to
    prevent the application from running in an unstable state.

    Returns:
        Settings: The validated application configuration.

    Raises:
        ConfigurationError: If any required environment variable is not set.
    """
    config = get_settings()
    required = [
        config.POSTGRES_USER,
        config.POSTGRES_PW,
        config.POSTGRES_DB,
        config.POSTGRES_HOST,
        config.POSTGRES_PORT,
        config.TELEGRAM_BOT_TOKEN,
        config.MAX_CONCURRENCY_QUEUE,
        config.OLLAMA_URL,
    ]
    if not all(required):
        raise ConfigurationError(
            "Missing required environment variables. Please check your .env file."
        )
    if not config.ALLOWED_TELEGRAM_USER_IDS:
        raise ConfigurationError(
            "No users are allowed to use the bot. Please set ALLOWED_TELEGRAM_USER_IDS in your .env file."
        )
