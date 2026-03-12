"""
End-to-End (E2E) integration tests for the Lio-Agent.

These tests validate the entire processing pipeline: message ingestion,
AI extraction via Ollama, and final persistence in PostgreSQL.
"""

import asyncio
import logging
import time
from datetime import datetime

import pytest

from src.core.database import DatabaseManager
from src.models.message import Message
from src.repositories.audit_logs import AuditLogsRepository
from src.repositories.expenses import ExpenseRepository
from src.services.llm import LlmService
from src.services.orchestrator import handle_telegram_update
from src.services.processor_queue import ProcessingQueue, start_worker_tasks

logger = logging.getLogger(__name__)


@pytest.fixture
def test_cases():
    """
    Returns a mix of valid financial messages and informal chat to test
    LLM extraction and filtering capabilities.
    """
    # 4 messages from user unauthorized and 9 messages from user authorized but 4 messages are not expenses
    return [
        {
            "user_id": 2061932691,
            "chat_id": 2061932691,
            "message_id": 1,
            "text": "Gasté 150000 en comida ayer pagando con Bancolombia Leidy",
        },
        {
            "user_id": 2061932691,
            "chat_id": 2061932691,
            "message_id": 2,
            "text": "Compré 2 cafés en Juan Valdez por 15000 pesos usando Nubank Yamile",
        },
        {
            "user_id": 2061932691,
            "chat_id": 2061932691,
            "message_id": 3,
            "text": "Pagué el arriendo de marzo por 1.200.000 con Bancolombia Leidy",
        },
        {
            "user_id": 2061932691,
            "chat_id": 2061932691,
            "message_id": 4,
            "text": "Fui al supermercado y gasté 250.000 pesos en víveres usando Nubank Mercado",
        },
        {
            "user_id": 2061932699,
            "chat_id": 2061932699,
            "message_id": 5,
            "text": "Me comí una hamburguesa por 35.000 pesos con Nequi Leidy",
        },
        {
            "user_id": 2061932699,
            "chat_id": 2061932699,
            "message_id": 6,
            "text": "Pagué el recibo de la luz de este mes por 120.000 pesos usando efectivo",
        },
        {
            "user_id": 2061932699,
            "chat_id": 2061932699,
            "message_id": 7,
            "text": "Compré una blusa en Zara por 89.900 pesos con Nubank Yamile",
        },
        {
            "user_id": 2061932699,
            "chat_id": 2061932699,
            "message_id": 8,
            "text": "Cené sushi con mi novio por 180.000 pesos pagando con Davivienda Yamile",
        },
        {
            "user_id": 2061932699,
            "chat_id": 2061932699,
            "message_id": 9,
            "text": "Me compré unos zapatos en la tienda de la esquina por 95.000 pesos usando efectivo",
        },
        {
            "user_id": 2061932699,
            "chat_id": 2061932699,
            "message_id": 10,
            "text": "Hola, como estás?",
        },
        {
            "user_id": 2061932699,
            "chat_id": 2061932699,
            "message_id": 11,
            "text": "Me puedes ayudar",
        },
        {
            "user_id": 2061932699,
            "chat_id": 2061932699,
            "message_id": 12,
            "text": "Cuanto he gastado este mes?",
        },
        {
            "user_id": 2061932699,
            "chat_id": 2061932699,
            "message_id": 13,
            "text": "Me alcanza para cenar?",
        },
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
async def test_e2e_flow(mocker, test_cases, mock_telegram_app):
    """
    Tests the full business flow: Input -> Queue -> AI -> Database.

    Validates that NLP extraction correctly identifies expenses and
    ignores non-financial communication.
    """
    # Arrange: Initialize repository, queue, and background workers
    db = DatabaseManager()
    await db.initialize()

    expense_repository = ExpenseRepository(db=db)
    await expense_repository.setup_schema()

    audit_logs_repository = AuditLogsRepository(db=db)
    await audit_logs_repository.setup_schema()

    processing_queue = ProcessingQueue()
    llm_service = LlmService()

    # Clean test database
    await expense_repository.delete_by_user_id(user_id=2061932699)
    await audit_logs_repository.delete_by_user_id(user_id=2061932691)

    worker_tasks = await start_worker_tasks(
        processing_queue=processing_queue,
        expense_repository=expense_repository,
        telegram_app=mock_telegram_app,
        llm_service=llm_service,
    )
    logger.info(f"Background processing started with {len(worker_tasks)} workers.")

    start_time = time.perf_counter()

    # It's necessary to create a mock update like the one in the Telegram API for each test case
    for test in test_cases:
        mock_update = mocker.Mock()
        mock_update.message.from_user.id = test["user_id"]
        mock_update.message.from_user.first_name = "Leidy"
        mock_update.message.from_user.last_name = "Acuña"
        mock_update.message.from_user.username = "leidyacunag"
        mock_update.message.chat.id = test["chat_id"]
        mock_update.message.text = test["text"]
        mock_update.message.message_id = test["message_id"]
        mock_update.message.date = datetime.now()
        mock_update.message.reply_text = mocker.AsyncMock()

        await handle_telegram_update(
            update=mock_update,
            context=mock_telegram_app,
            processing_queue=processing_queue,
            audit_logs_repository=audit_logs_repository,
        )

    # Wait for the queue to be fully processed by the workers
    await processing_queue.join()

    end_time = time.perf_counter()
    duration = end_time - start_time

    # Assert: Verify total valid records in DB and performance
    logger.info(f"Processed messages in {duration:.2f} seconds")

    count = await expense_repository.get_total_count_by_user_id(user_id=2061932699)
    # 5 messages should be valid expenses, 8 should be filtered out
    assert count == 5

    count_audit_logs = await audit_logs_repository.get_total_count_by_user_id(
        user_id=2061932691
    )
    # 4 messages should be valid audit logs, 9 should be filtered out
    assert count_audit_logs == 4

    # Cleanup: Shutdown DB connections
    await db.shutdown()
