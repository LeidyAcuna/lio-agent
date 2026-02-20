import asyncio
import logging
from typing import Callable, List

from core.config import get_settings
from core.exceptions import AppError
from models.message import Message
from repository.expenses import ExpenseRepository
from services.orchestrator import process_expense_message

settings = get_settings()

logger = logging.getLogger(__name__)


class ProcessingQueue:
    """
    Manages an asynchronous queue for processing messages.

    Uses a semaphore to limit concurrent AI processing, ensuring system
    resources are managed according to the MAX_CONCURRENCY_QUEUE setting.
    """

    def __init__(self) -> None:
        """Initializes the queue and limiting semaphore."""
        self.queue: asyncio.Queue[Message] = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(int(settings.MAX_CONCURRENCY_QUEUE))

    async def enqueue(self, message: Message) -> None:
        """
        Adds a message to the processing queue.

        Args:
            message (Message): The message to be processed.
        """
        await self.queue.put(message)
        logger.info(f"Message {message.message_id} enqueued successfully.")

    async def dequeue(self) -> Message:
        """
        Retrieves the next message from the queue.

        Returns:
            Message: The next message to process.
        """
        return await self.queue.get()

    def task_done(self) -> None:
        """Signals that a previously enqueued task is complete."""
        self.queue.task_done()


async def message_worker(
    worker_id: str,
    queue_manager: ProcessingQueue,
    expense_repository: ExpenseRepository,
    telegram_app,
) -> None:
    """
    Background worker that consumes and processes messages from the queue.

    Args:
        worker_id (str): Unique identifier for the worker instance.
        queue_manager (ProcessingQueue): The queue to pull messages from.
        expense_repository (ExpenseRepository): Repository for data persistence.
        telegram_app: The Telegram application instance for sending responses.
    """
    while True:
        message = await queue_manager.dequeue()
        try:
            async with queue_manager.semaphore:
                logger.info(
                    f"Worker {worker_id} processing message {message.message_id}"
                )

                await process_expense_message(
                    expense_repository=expense_repository,
                    message=message,
                    telegram_app=telegram_app,
                )

                logger.info(f"Worker {worker_id} finished message {message.message_id}")

        except AppError as e:
            logger.error(f"Domain error in {worker_id}: {e.to_dict()}")
        except Exception as e:
            logger.critical(f"Unexpected error in {worker_id}: {str(e)}", exc_info=True)
        finally:
            queue_manager.task_done()


async def start_worker_tasks(
    queue_manager: ProcessingQueue, expense_repository: ExpenseRepository, telegram_app
) -> List[asyncio.Task]:
    """
    Spawns multiple worker tasks based on concurrency settings.

    Args:
        queue_manager (ProcessingQueue): The shared queue for workers.
        expense_repository (ExpenseRepository): Data repository for workers.
        telegram_app: Telegram app instance.

    Returns:
        List[asyncio.Task]: A list of the created background tasks.
    """
    worker_tasks = []
    concurrency = int(settings.MAX_CONCURRENCY_QUEUE)

    for i in range(concurrency):
        task = asyncio.create_task(
            message_worker(
                worker_id=f"worker-{i}",
                queue_manager=queue_manager,
                expense_repository=expense_repository,
                telegram_app=telegram_app,
            )
        )
        worker_tasks.append(task)

    logger.info(f"Spawned {concurrency} background workers.")
    return worker_tasks
