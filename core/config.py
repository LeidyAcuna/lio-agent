import os

from core.exceptions.base import ConfigurationError


class Settings:
    """
    Configuration settings for the application.

    This class loads environment variables required for database connection,
    Telegram bot integration, and concurrency management.
    """

    POSTGRES_USER: str = os.getenv("DB_USER")
    POSTGRES_PW: str = os.getenv("DB_PASS")
    POSTGRES_DB: str = os.getenv("DB_NAME")
    SERVICE_POSTGRES_HOST: str = os.getenv("DB_HOST")
    SERVICE_POSTGRES_PORT: str = os.getenv("DB_PORT")
    TELEGRAM_BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    MAX_CONCURRENCY_QUEUE: str = os.getenv("MAX_CONCURRENCY")


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
        config.SERVICE_POSTGRES_HOST,
        config.SERVICE_POSTGRES_PORT,
        config.TELEGRAM_BOT_TOKEN,
        config.MAX_CONCURRENCY_QUEUE,
    ]
    if not all(required):
        raise ConfigurationError(
            "Missing required environment variables. Please check your .env file."
        )
