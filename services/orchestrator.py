import logging

from telegram import Update
from telegram.ext import ContextTypes

from core.exceptions.base import AppError
from models.message import Message
from repository.expenses import ExpenseRepository
from services.llm import extract_expense_from_text

logger = logging.getLogger(__name__)


async def process_expense_message(
    expense_repository: ExpenseRepository, message: Message, telegram_app
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
        expense_data = await extract_expense_from_text(user_input=message.text)

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

        # Canonicalize the TG message into our domain Message model
        domain_message = Message(
            user_id=update.message.from_user.id,
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
