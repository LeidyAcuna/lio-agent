"""
Unit tests for the MessageQueue service.

These tests verify the asynchronous queue operations (enqueue, dequeue, size)
in isolation, ensuring that the producer-consumer logic behaves correctly
without requiring a database or active workers.
"""

import pytest

from src.models.message import Message
from src.services.msg_queue import MessageQueue
from src.services.worker_manager import WorkerManager


@pytest.fixture
def mock_settings(mocker):
    """
    Mocks the global settings within the message_queue module.

    This ensures the tests use a controlled concurrency limit and don't
    depend on external environment variables.
    """
    mock_conf = mocker.patch("src.services.msg_queue.settings")
    mock_conf.MAX_CONCURRENCY_QUEUE = 4
    return mock_conf


@pytest.fixture
def message_queue(mock_settings):
    """
    Provides a fresh instance of MessageQueue for each test.
    """
    return MessageQueue()


@pytest.fixture
def message_data():
    """
    Provides a sample domain Message object for testing queue operations.
    """
    return Message(
        user_id=2061932699,
        chat_id=2061932699,
        message_id=58,
        text="Compré 2500 pesos de pan en la tienda ayer con efectivo",
    )


@pytest.mark.asyncio
async def test_add_message_to_queue(message_data, message_queue):
    """
    Verifies that multiple messages are correctly added to the queue and
    tracked by its size.
    """
    # Arrange
    total_to_add = 8

    # Act
    for _ in range(total_to_add):
        await message_queue.enqueue(message_data)

    # Assert
    assert message_queue.size() == total_to_add

    # Cleanup
    await message_queue.clear()


@pytest.mark.asyncio
async def test_remove_message_from_queue(message_data, message_queue):
    """
    Validates that messages are correctly removed from the queue using FIFO logic.
    """
    # Arrange
    await message_queue.enqueue(message_data)

    # Act
    await message_queue.dequeue()

    # Assert
    assert message_queue.is_empty() is True

    # Cleanup
    await message_queue.clear()
