from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from src.core.config import get_settings
from src.repository.audit_logs import AuditLogsRepository
from src.services.orchestrator import handle_telegram_update
from src.services.processor_queue import ProcessingQueue

settings = get_settings()


class TelegramBot:
    """
    Wrapper class for the Telegram Application.

    Handles the initialization of the bot application and registration
    of message handlers.
    """

    def __init__(self) -> None:
        """
        Initializes the Telegram application using the provided bot token.
        """
        self.app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    def setup_handlers(
        self, queue_manager: ProcessingQueue, audit_logs_repository: AuditLogsRepository
    ) -> None:
        """
        Registers handlers to process incoming Telegram messages.

        Args:
            queue_manager (ProcessingQueue): The queue where incoming messages
                                          will be placed for processing.
        """

        async def message_handler(
            update: Update, context: ContextTypes.DEFAULT_TYPE
        ) -> None:
            """Internal wrapper to bridge Telegram updates with the manager."""
            await handle_telegram_update(
                update, context, queue_manager, audit_logs_repository
            )

        # Handler for all text messages that are not commands
        text_handler = MessageHandler(
            filters.TEXT & (~filters.COMMAND), message_handler
        )
        self.app.add_handler(text_handler)
        # self.telegram_app.run_polling()
