import asyncio
import logging
from typing import List

from src.core.config import get_settings
from src.core.exceptions import AppError
from src.models.message import Message

settings = get_settings()

logger = logging.getLogger(__name__)


class MessageQueue:
    """
    Manages an asynchronous queue.

    Uses a semaphore to limit concurrent AI processing, ensuring system
    resources are managed according to the MAX_CONCURRENCY_QUEUE setting.
    """

    def __init__(self) -> None:
        """Initializes the queue and limiting semaphore."""
        self.queue: asyncio.Queue[Message] = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY_QUEUE)

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

    def is_empty(self) -> bool:
        """Checks if the queue is empty."""
        return self.queue.empty()

    def size(self) -> int:
        """Returns the number of messages in the queue."""
        return self.queue.qsize()

    async def clear(self) -> None:
        """Clears all messages from the queue."""
        while not self.queue.empty():
            await self.queue.get()

    async def join(self) -> None:
        """Waits for all messages in the queue to be processed."""
        await self.queue.join()

    def task_done(self) -> None:
        """Signals that a previously enqueued task is complete."""
        self.queue.task_done()
