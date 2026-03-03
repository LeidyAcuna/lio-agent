import pytest

from src.core.config import Settings
from src.models.message import Message
from src.services.processor_queue import ProcessingQueue


@pytest.fixture
def mock_settings(mocker):
    """Mock settings for the test."""
    mock_conf = mocker.patch("src.services.processor_queue.settings")
    mock_conf.MAX_CONCURRENCY_QUEUE = "4"
    return mock_conf


@pytest.fixture
def processing_queue(mock_settings):
    return ProcessingQueue()


@pytest.fixture
def message_data():
    return Message(
        user_id=2061932699,
        chat_id=2061932699,
        message_id=58,
        text="Compré 2500 pesos de pan en la tienda ayer con efectivo",
    )


@pytest.mark.asyncio
async def test_add_message_to_queue(message_data, processing_queue):
    total_to_add = 8
    for _ in range(total_to_add):
        await processing_queue.enqueue(message_data)
    assert await processing_queue.size() == total_to_add
    await processing_queue.clear()


@pytest.mark.asyncio
async def test_remove_message_from_queue(message_data, processing_queue):
    await processing_queue.enqueue(message_data)
    await processing_queue.dequeue()
    assert await processing_queue.is_empty() is True
    await processing_queue.clear()
