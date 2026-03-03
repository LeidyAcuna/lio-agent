"""
End-to-End (E2E) integration tests for the Lio-Agent.

These tests validate the entire processing pipeline: message ingestion,
AI extraction via Ollama, and final persistence in PostgreSQL.
"""

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
    """
    Returns a mix of valid financial messages and informal chat to test
    LLM extraction and filtering capabilities.
    """
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
    """
    Mocks the Telegram application to avoid real network calls during E2E tests,
    while still allowing the bot to 'reply' to simulated messages.
    """
    mock_app = mocker.Mock()
    mock_app.bot = mocker.Mock()
    mock_app.bot.send_message = mocker.AsyncMock()
    return mock_app


@pytest.mark.asyncio
async def test_e2e_flow(test_cases, mock_telegram_app):
    """
    Tests the full business flow: Input -> Queue -> AI -> Database.

    Validates that NLP extraction correctly identifies expenses and
    ignores non-financial communication.
    """
    # Arrange: Initialize repository, queue, and background workers
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

    # Clean test database
    async with expense_repository.db.get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM expenses")

    start_time = time.perf_counter()

    # Act: Enqueue all test messages
    for i, text in enumerate(test_cases):
        domain_message = Message(
            user_id=2061932699,
            chat_id=2061932699,
            message_id=i,
            text=text,
        )
        await queue_manager.enqueue(message=domain_message)

    # Wait for the queue to be fully processed by the workers
    await queue_manager.join()

    end_time = time.perf_counter()
    duration = end_time - start_time

    # Assert: Verify total valid records in DB and performance
    logger.info(f"\n🚀 Processed {len(test_cases)} messages in {duration:.2f} seconds")
    logger.info(f"⚡ Speed: {len(test_cases) / duration:.2f} messages/second")

    count = await expense_repository.get_total_count()
    # 9 messages should be valid expenses, 4 should be filtered out
    assert count == 9

    # Cleanup: Shutdown DB connections
    await expense_repository.db.shutdown()
