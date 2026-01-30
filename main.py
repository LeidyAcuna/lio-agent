import asyncio
from repository.data import ManagerDB
from services.asqueue import QueueManager, tasks
from services.bot import TelegramBot


async def main():
    # Preparation phase - Inicializing manager for db, queue and bot
    print("Hello from lio-agent!")
    db_manager = ManagerDB()
    queue_manager = QueueManager()
    telegram_bot = TelegramBot()

    db_manager.init_db()
    print("DB inicialized succesfully!")

    # Define telegram bot with filters and handler
    telegram_bot.get_updates_bot(queue_manager=queue_manager)   

    # Run to workers for preparing to job
    mtasks = await tasks(queue_manager=queue_manager, db_manager=db_manager, telegram_app=telegram_bot.app)
    print(f"Executing {len(mtasks)} workers")

    # Guarantee the bot was starting and stoping correctly
    async with telegram_bot.app:
        # Starting the bot
        await telegram_bot.app.initialize()
        await telegram_bot.app.start()

        await telegram_bot.app.updater.start_polling()
        # Creamos nuestra propia "ancla" ⚓
        stop_event = asyncio.Event()
        print("Bot escuchando... Usa Ctrl+C para detenerlo.")

        try:
            # El programa se quedará aquí "esperando la señal"
            # permitiendo que los workers y el bot sigan procesando
            await stop_event.wait()
        except (KeyboardInterrupt, SystemError):
            print("Deteniendo...")
        finally:
            # Primero detenemos el polling para que no lance el error de "Application still running"
            await telegram_bot.app.updater.stop()
            await telegram_bot.app.stop()
            await telegram_bot.app.shutdown()





if __name__ == "__main__":
    # asyncio.run es el único que maneja el loop de forma global
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
