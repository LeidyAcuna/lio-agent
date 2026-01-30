import asyncio
import logging
from typing import Callable, List
from models.message import Message
from core.config import get_settings
from services.manager import execute_process

settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('db_init')

class QueueManager():
    """
    Manage the queue for saving messages and semaphore for guarantee that only max number use the machine
    resources at the same time for processing with IA
    """
    def __init__(self) -> None:
        self.queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(int(settings.MAX_CONCURRENCY_QUEUE))

    async def enqueue(self, message: Message) -> None:
        await self.queue.put(message)
        logger.info("The message was enqueued successfully!")

    async def dequeue(self) -> Message:
        return await self.queue.get()

    def task_done(self) -> None:
        self.queue.task_done()



async def worker(worker_id: str, queue_manager, db_manager, telegram_app):
    """Consumer for working always getting a message of queue and send to process with IA"""
    while True:
        message = await queue_manager.dequeue()
        try:
            async with queue_manager.semaphore:
                logger.info(f"Worker {worker_id} is processing message {message.message_id}")
                await execute_process(db_manager=db_manager, message=message, telegram_app=telegram_app)
                logger.info(f"Worker {worker_id} is ready with {message.message_id}")

        except Exception as e:
            logger.error(f"Error in {worker_id}: {e}")
        finally:
            queue_manager.task_done()


async def tasks(queue_manager, db_manager, telegram_app) -> List:
    """
    Define 1 to 1 with max concurrency queue and workers numbers for working in background
    """
    tasks = []
    for i in range(int(settings.MAX_CONCURRENCY_QUEUE)):
        task = asyncio.create_task(
            worker(
                    worker_id=f'worker-{i}', 
                    queue_manager=queue_manager, 
                    db_manager=db_manager,
                    telegram_app=telegram_app
                )
            )
        tasks.append(task)
    return tasks
