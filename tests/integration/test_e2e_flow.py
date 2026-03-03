import asyncio
import logging
import time

import pytest

from src.models.message import Message
from src.repository.expenses import ExpenseRepository
from src.services.processor_queue import ProcessingQueue, start_worker_tasks

logger = logging.getLogger(__name__)


@pytest.fixture
def test_cases():
    return [
        "Gasté 150000 en comida ayer pagando con Bancolombia Leidy",
        "Compré 2 cafés en Juan Valdez por 15000 pesos usando Nubank Yamile",
        "Pagué el arriendo de marzo por 1.200.000 con Bancolombia Leidy",
        "Fui al supermercado y gasté 250.000 pesos en víveres usando Nubank Mercado",
        "Me comí una hamburguesa por 35.000 pesos con Nequi Leidy",
        "Pagué el recibo de la luz de este mes por 120.000 pesos usando efectivo",
        "Compré una blusa en Zara por 89.900 pesos con Nubank Yamile",
        "Cené sushi con mi novio por 180.000 pesos pagando con Davivienda Yamile",
        "Me compré unos zapatos en la tienda de la esquina por 95.000 pesos usando efectivo",
        "Hola, como estás?",
        "Me puedes ayudar",
        "Cuanto he gastado este mes?",
        "Me alcanza para cenar?",
    ]


@pytest.fixture
def mock_telegram_app(mocker):
    mock_telegram_app = mocker.Mock()
    mock_telegram_app.bot = mocker.Mock()
    mock_telegram_app.bot.send_message = mocker.AsyncMock()
    return mock_telegram_app


@pytest.mark.asyncio
async def test_e2e_flow(test_cases, mock_telegram_app):

    expense_repository = ExpenseRepository()
    await expense_repository.db.initialize()
    await expense_repository.setup_schema()
    queue_manager = ProcessingQueue()

    worker_tasks = await start_worker_tasks(
        queue_manager=queue_manager,
        expense_repository=expense_repository,
        telegram_app=mock_telegram_app,
    )
    logger.info(f"Background processing started with {len(worker_tasks)} workers.")

    # 1. Clean DB test
    async with expense_repository.db.get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM expenses")

    tasks = []
    start_time = time.perf_counter()

    # 2. Insert 1000 messages
    for i, text in enumerate(test_cases):
        domain_message = Message(
            user_id=2061932699,
            chat_id=2061932699,
            message_id=i,
            text=text,
        )
        await queue_manager.enqueue(message=domain_message)

    await queue_manager.join()

    end_time = time.perf_counter()
    duration = end_time - start_time

    # 3. Assert: Robustness checks
    logger.info(f"\n🚀 Processed {len(test_cases)} messages in {duration:.2f} seconds")
    logger.info(f"⚡ Speed: {len(test_cases) / duration:.2f} messages/second")

    # Verify that they are actually in the DB
    count = await expense_repository.get_total_count()
    assert count == 9

    await expense_repository.db.shutdown()
