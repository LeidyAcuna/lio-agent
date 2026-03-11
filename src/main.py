import asyncio
import logging
import os

import debugpy

from src.core.config import validate_settings
from src.core.database import DatabaseManager
from src.core.exceptions import AppError
from src.repository.audit_logs import AuditLogsRepository
from src.repository.expenses import ExpenseRepository
from src.services.bot import TelegramBot
from src.services.llm import LlmService
from src.services.processor_queue import ProcessingQueue, start_worker_tasks

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_application():
    """
    Main entry point for the Lio-Agent application.

    This function coordinates the initialization of all core components:
    1. Establishes database connections and initializes the schema.
    2. Sets up the asynchronous processing queue.
    3. Configures the Telegram bot and its message handlers.
    4. Starts the background worker tasks for processing messages.
    5. Runs the bot's polling loop until a termination signal is received.
    """
    try:
        logger.info("Initializing Lio-Agent core services...")
        validate_settings()
        # Initialize Infrastructure
        db = DatabaseManager()
        await db.initialize()

        expense_repository = ExpenseRepository(db=db)
        audit_logs_repository = AuditLogsRepository(db=db)

        # Database schema verification/setup
        await expense_repository.setup_schema()
        await audit_logs_repository.setup_schema()
        logger.info("Infrastructure initialized successfully.")

        processing_queue = ProcessingQueue()
        bot_service = TelegramBot()
        llm_service = LlmService()

        # Register bot handlers
        bot_service.setup_handlers(
            queue_manager=processing_queue, audit_logs_repository=audit_logs_repository
        )

        # Start background workers
        worker_tasks = await start_worker_tasks(
            queue_manager=processing_queue,
            expense_repository=expense_repository,
            telegram_app=bot_service.app,
            llm_service=llm_service,
        )
        logger.info(f"Background processing started with {len(worker_tasks)} workers.")

        # Start the Telegram Bot lifecycle
        async with bot_service.app:
            await bot_service.app.initialize()
            await bot_service.app.start()
            await bot_service.app.updater.start_polling()

            # Use an event to keep the application alive during polling
            stop_event = asyncio.Event()
            logger.info("Bot is active and listening. Use Ctrl+C to shut down.")

            try:
                # Wait forever until interrupted
                await stop_event.wait()
            except KeyboardInterrupt, SystemError:
                logger.info("Shutdown signal received.")
            finally:
                logger.info("Closing bot services...")
                await bot_service.app.updater.stop()
                await bot_service.app.stop()
                await bot_service.app.shutdown()

        logger.info("Closing database connections...")
        await db.shutdown()

    except AppError as e:
        logger.critical(f"Application failed to start: {e.to_dict()}", exc_info=True)
    except Exception as e:
        logger.critical(
            f"Unrecoverable error during execution: {str(e)}", exc_info=True
        )


if __name__ == "__main__":
    # Optional Debug Mode configuration
    if os.getenv("DEBUG_MODE") == "true":
        debugpy.listen(("0.0.0.0", 5677))
        print("Waiting for debugger to attach...")
        debugpy.wait_for_client()

    try:
        asyncio.run(run_application())
    except KeyboardInterrupt:
        logger.info("Application stopped by user.")
