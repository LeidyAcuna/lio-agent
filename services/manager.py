from telegram import Update
from telegram.ext import ContextTypes

from services.llm import test_ollama
from models.message import Message

async def execute_process(db_manager, message: Message, telegram_app):
    obj_expense = test_ollama(user_input=message.text)
    db_manager.insert_row_in_db(user_id=message.user_id, object=obj_expense)
    await telegram_app.bot.send_message(
        chat_id=message.chat_id,
        text="El gasto se ha registrado con éxito",
        reply_to_message_id=message.message_id
    )

async def attend_to_new_messages(update: Update, context: ContextTypes.DEFAULT_TYPE, queue_manager):
    message = Message(
        user_id=update.message.from_user.id,
        chat_id=update.message.chat.id,
        message_id=update.message.message_id,
        text=update.message.text
    )
    await queue_manager.enqueue(message=message)


