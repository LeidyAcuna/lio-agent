import os

from core.exceptions import ConfigurationError


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
    TOKEN_TELEGRAM_BOT: str = os.getenv("TOKEN_BOT")
    MAX_CONCURRENCY_QUEUE: str = os.getenv("MAX_CONCURRENCY")


_settings = Settings()


def get_settings() -> Settings:
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
    if not all(
        [
            _settings.POSTGRES_USER,
            _settings.POSTGRES_PW,
            _settings.POSTGRES_DB,
            _settings.SERVICE_POSTGRES_HOST,
            _settings.SERVICE_POSTGRES_PORT,
            _settings.TOKEN_TELEGRAM_BOT,
            _settings.MAX_CONCURRENCY_QUEUE,
        ]
    ):
        raise ConfigurationError(
            "Missing required environment variables. Please check your .env file."
        )
    return _settings
