import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.core.config import get_settings
from src.core.exceptions import AppError
from src.models.audit_log import AuditLog
from src.models.message import Message

settings = get_settings()

logger = logging.getLogger(__name__)


class Orchestrator:

    def __init__(self, msg_queue, audit_logs_repository):
        self.msg_queue = msg_queue
        self.audit_logs_repository = audit_logs_repository

    async def handle_telegram_update(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Entry point for new Telegram messages.

        Converts the Telegram update into a domain Message and places it in the
        asynchronous processing queue.

        Args:
            update (Update): The raw update from Telegram API.
            context (ContextTypes.DEFAULT_TYPE): The callback context.
        """
        if not update.message or not update.message.from_user:
            return

        try:
            logger.info(f"New Telegram update received: ID {update.message.message_id}")

            user_id = update.message.from_user.id
            if user_id not in settings.ALLOWED_TELEGRAM_USER_IDS:
                await self.handle_unauthorized_user(update=update)
                return

            domain_message = Message(
                user_id=user_id,
                chat_id=update.message.chat.id,
                message_id=update.message.message_id,
                text=update.message.text,
            )

            await self.msg_queue.enqueue(message=domain_message)

        except AppError as e:
            logger.error(f"Error enqueuing message {update.message.message_id}: {e}")
            await update.message.reply_text(
                "⚠️ Lo siento, tuve un problema interno al recibir tu mensaje. Intenta de nuevo en unos momentos."
            )

    async def handle_unauthorized_user(self, update: Update) -> None:
        """
        Handles unauthorized user messages.

        Args:
            update (Update): The raw update from Telegram API.
        """
        try:
            first_name = update.message.from_user.first_name or None
            last_name = update.message.from_user.last_name or None
            username = update.message.from_user.username or None

            audit_log = AuditLog(
                user_id=update.message.from_user.id,
                fullname=(
                    f"{first_name} {last_name}" if first_name and last_name else None
                ),
                username=username,
                chat_id=update.message.chat.id,
                message_text=update.message.text,
                message_date=update.message.date,
            )
            await self.audit_logs_repository.create(audit_log)
            logger.warning(f"Unauthorized user: {update.message.from_user.id}")
            await update.message.reply_text(
                "⚠️ Lo siento, no tienes permiso para usar este bot."
            )
        except Exception as e:
            logger.error(f"Error handling unauthorized user: {e}")
