from telegram.ext import ApplicationBuilder, MessageHandler, filters

from core.config import get_settings
from services.manager import attend_to_new_messages

settings = get_settings()


class TelegramBot:
    def __init__(self) -> None:
        self.app = ApplicationBuilder().token(settings.TOKEN_TELEGRAM_BOT).build()

    def get_updates_bot(self, queue_manager):
        async def handler_wrapper(update, context):
            await attend_to_new_messages(update, context, queue_manager)

        new_messages_handler = MessageHandler(
            filters.TEXT & (~filters.COMMAND), handler_wrapper
        )
        self.app.add_handler(new_messages_handler)
        # self.telegram_app.run_polling()
