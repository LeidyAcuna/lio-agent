import os


class Settings:
    POSTGRES_USER: str = os.getenv("DB_USER")
    POSTGRES_PW: str = os.getenv("DB_PASS")
    POSTGRES_DB: str = os.getenv("DB_NAME")
    SERVICE_POSTGRES_HOST: str = os.getenv("DB_HOST")
    SERVICE_POSTGRES_PORT: str = os.getenv("DB_PORT")
    TOKEN_TELEGRAM_BOT: str = os.getenv("TOKEN_BOT")
    MAX_CONCURRENCY_QUEUE: str = os.getenv("MAX_CONCURRENCY")


_settings = Settings()


def get_settings():
    print("Loading config settings from environment")
    return _settings
