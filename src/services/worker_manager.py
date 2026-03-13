import asyncio
import logging
from typing import List

from src.core.config import get_settings
from src.core.exceptions import AppError
from src.models.message import Message
from src.repositories.expenses import ExpenseRepository
from src.services.expense_processor import ExpenseProcessor

settings = get_settings()

logger = logging.getLogger(__name__)


class WorkerManager:
    """
    Processes messages from an asynchronous queue.
    """

    def __init__(
        self,
        queue: asyncio.Queue[Message],
        expense_processor,
    ) -> None:
        self.queue = queue
        self.expense_processor = expense_processor

    async def start_worker_tasks(self) -> List[asyncio.Task]:
        """
        Spawns multiple worker tasks based on concurrency settings.

        Returns:
            List[asyncio.Task]: A list of the created background tasks.
        """
        worker_tasks = []
        concurrency = settings.MAX_CONCURRENCY_QUEUE

        for i in range(concurrency):
            task = asyncio.create_task(self.process_message(worker_id=f"worker-{i}"))
            worker_tasks.append(task)

        logger.info(f"Spawned {concurrency} background workers.")
        return worker_tasks

    async def process_message(self, worker_id: str) -> None:
        """
        Background worker that consumes and processes messages from the queue.

        Args:
            worker_id (str): Unique identifier for the worker instance.
        """
        while True:
            message = await self.queue.dequeue()
            try:
                async with self.queue.semaphore:
                    logger.info(
                        f"Worker {worker_id} processing message {message.message_id}"
                    )

                    await self.expense_processor.process_expense_message(
                        message=message
                    )

                    logger.info(
                        f"Worker {worker_id} finished message {message.message_id}"
                    )

            except AppError as e:
                logger.error(f"Domain error in {worker_id}: {e.to_dict()}")
            except Exception as e:
                logger.critical(
                    f"Unexpected error in {worker_id}: {str(e)}", exc_info=True
                )
            finally:
                self.queue.task_done()
