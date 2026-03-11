import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.core.config import get_settings
from src.core.exceptions import AppError
from src.models.audit_log import AuditLog
from src.models.message import Message
from src.repository.expenses import ExpenseRepository

settings = get_settings()

logger = logging.getLogger(__name__)


async def process_expense_message(
    expense_repository: ExpenseRepository, message: Message, telegram_app, llm_service
) -> None:
    """
    Coordinates the full flow of processing an expense message.

    1. Extracts data using LLM.
    2. Persists the expense in the database.
    3. Notifies the user of the result via Telegram.

    Args:
        expense_repository (ExpenseRepository): Data persistence layer.
        message (Message): The domain message model to process.
        telegram_app: The Telegram application instance.
    """
    try:
        # Step 1: Extract data using IA
        expense_data = await llm_service.extract_expense_from_text(
            user_input=message.text
        )

        # Step 2: Save to database
        await expense_repository.create(user_id=message.user_id, expense=expense_data)

        # Step 3: Success notification
        await telegram_app.bot.send_message(
            chat_id=message.chat_id,
            text="✅ ¡Gasto registrado con éxito!",
            reply_to_message_id=message.message_id,
        )
        logger.info(
            f"Successfully processed message {message.message_id} for user {message.user_id}"
        )

    except AppError as e:
        logger.error(
            f"Domain error processing message {message.message_id}: {e.message}"
        )

        # User-friendly error message
        await telegram_app.bot.send_message(
            chat_id=message.chat_id,
            text="❌ No pude procesar tu mensaje. Por favor, intenta de nuevo con más detalles.",
            reply_to_message_id=message.message_id,
        )


async def handle_telegram_update(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    processing_queue,
    audit_logs_repository,
) -> None:
    """
    Entry point for new Telegram messages.

    Converts the Telegram update into a domain Message and places it in the
    asynchronous processing queue.

    Args:
        update (Update): The raw update from Telegram API.
        context (ContextTypes.DEFAULT_TYPE): The callback context.
        processing_queue: The queue to enqueue the message.
    """
    if not update.message or not update.message.from_user:
        return

    try:
        logger.info(f"New Telegram update received: ID {update.message.message_id}")

        user_id = update.message.from_user.id
        if user_id not in settings.ALLOWED_TELEGRAM_USER_IDS:
            await handle_unauthorized_user(update, audit_logs_repository)
            return
        # Canonicalize the TG message into our domain Message model
        domain_message = Message(
            user_id=user_id,
            chat_id=update.message.chat.id,
            message_id=update.message.message_id,
            text=update.message.text,
        )

        await processing_queue.enqueue(message=domain_message)

    except AppError as e:
        logger.error(f"Error enqueuing message {update.message.message_id}: {e}")
        await update.message.reply_text(
            "⚠️ Lo siento, tuve un problema interno al recibir tu mensaje. Intenta de nuevo en unos momentos."
        )


async def handle_unauthorized_user(update: Update, audit_logs_repository) -> None:
    """
    Handles unauthorized user messages.

    Args:
        update (Update): The raw update from Telegram API.
        audit_logs_repository: The audit logs repository.
    """
    try:
        first_name = update.message.from_user.first_name or None
        last_name = update.message.from_user.last_name or None
        username = update.message.from_user.username or None

        audit_log = AuditLog(
            user_id=update.message.from_user.id,
            fullname=f"{first_name} {last_name}" if first_name and last_name else None,
            username=username,
            chat_id=update.message.chat.id,
            message_text=update.message.text,
            message_date=update.message.date,
        )
        await audit_logs_repository.create(audit_log)
        logger.warning(f"Unauthorized user: {update.message.from_user.id}")
        await update.message.reply_text(
            "⚠️ Lo siento, no tienes permiso para usar este bot."
        )
    except Exception as e:
        logger.error(f"Error handling unauthorized user: {e}")
