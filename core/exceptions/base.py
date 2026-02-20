from typing import Any, Optional


class AppError(Exception):

    code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message or self.message
        self.code = code or self.code
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class ExternalServiceError(AppError):
    code = "external_service_error"
    message = "An error occurred with an external provider."


class TelegramAPIError(ExternalServiceError):
    code = "telegram_api_error"
    message = "Failed to communicate with Telegram servers."


class OllamaServiceError(ExternalServiceError):
    code = "ollama_service_error"
    message = "Ollama service is unreachable or returned an error."


class DatabaseError(AppError):
    code = "database_error"
    message = "Database operation error."


class DatabaseConnectionError(DatabaseError):
    code = "db_connection_error"
    message = "Could not establish a connection to the database."


class DatabaseInsertError(DatabaseError):
    code = "db_insert_error"
    message = "The information could not be saved in the database."


class AIError(AppError):
    code = "ai_error"
    message = "Error in AI processing."


class AIProcessingError(AIError):
    code = "ai_parsing_error"
    message = "The AI could not understand or structure the message."


class ValidationError(AppError):
    code = "validation_error"
    message = "The provided data is not valid."


class ConfigurationError(AppError):
    code = "config_error"
    message = "A required configuration or environment variable is missing."
