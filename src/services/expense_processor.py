import logging

from src.core.exceptions import AppError
from src.models.message import Message

logger = logging.getLogger(__name__)


class ExpenseProcessor:
    """
    Coordinates the full flow of processing an expense message.

    1. Extracts data using LLM.
    2. Persists the expense in the database.
    3. Notifies the user of the result via Telegram.
    """

    def __init__(self, expense_repository, telegram_app, llm_service) -> None:
        self.expense_repository = expense_repository
        self.telegram_app = telegram_app
        self.llm_service = llm_service

    async def process_expense_message(self, message: Message) -> None:
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
            expense_data = await self.llm_service.extract_expense_from_text(
                user_input=message.text
            )

            await self.expense_repository.create(
                user_id=message.user_id, expense=expense_data
            )

            await self.telegram_app.bot.send_message(
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

            await self.telegram_app.bot.send_message(
                chat_id=message.chat_id,
                text="❌ No pude procesar tu mensaje. Por favor, intenta de nuevo con más detalles.",
                reply_to_message_id=message.message_id,
            )
