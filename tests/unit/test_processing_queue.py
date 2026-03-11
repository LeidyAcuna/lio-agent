"""
Unit tests for the ProcessingQueue service.

These tests verify the asynchronous queue operations (enqueue, dequeue, size)
in isolation, ensuring that the producer-consumer logic behaves correctly
without requiring a database or active workers.
"""

import pytest

from src.models.message import Message
from src.services.processor_queue import ProcessingQueue


@pytest.fixture
def mock_settings(mocker):
    """
    Mocks the global settings within the processor_queue module.

    This ensures the tests use a controlled concurrency limit and don't
    depend on external environment variables.
    """
    mock_conf = mocker.patch("src.services.processor_queue.settings")
    mock_conf.MAX_CONCURRENCY_QUEUE = 4
    return mock_conf


@pytest.fixture
def processing_queue(mock_settings):
    """
    Provides a fresh instance of ProcessingQueue for each test.
    """
    return ProcessingQueue()


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
async def test_add_message_to_queue(message_data, processing_queue):
    """
    Verifies that multiple messages are correctly added to the queue and
    tracked by its size.
    """
    # Arrange
    total_to_add = 8

    # Act
    for _ in range(total_to_add):
        await processing_queue.enqueue(message_data)

    # Assert
    assert processing_queue.size() == total_to_add

    # Cleanup
    await processing_queue.clear()


@pytest.mark.asyncio
async def test_remove_message_from_queue(message_data, processing_queue):
    """
    Validates that messages are correctly removed from the queue using FIFO logic.
    """
    # Arrange
    await processing_queue.enqueue(message_data)

    # Act
    await processing_queue.dequeue()

    # Assert
    assert processing_queue.is_empty() is True

    # Cleanup
    await processing_queue.clear()
