"""
Integration tests for database stress testing.

This module evaluates the system's performance and robustness by simulating
high-concurrency write operations to a real PostgreSQL database.
"""

import asyncio
import time

import pytest

from src.models.expense import CategoryEnum, Expense, SourceEnum
from src.repository.expenses import ExpenseRepository


@pytest.mark.asyncio
async def test_stress_db_insertion():
    """
    Measures the database insertion speed under high concurrency.

    This test executes 1000 parallel insert operations to verify that the
    connection pool and repository can handle heavy loads without corruption.
    """
    # Arrange: Setup repository and clean test environment
    TOTAL_MESSAGES = 1000
    manager = ExpenseRepository()
    await manager.db.initialize()
    await manager.setup_schema()

    async with manager.db.get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM expenses")

    tasks = []
    start_time = time.perf_counter()

    # Act: Dispatch 1000 insertions in parallel
    for i in range(TOTAL_MESSAGES):
        expense = Expense(
            total=100.0,
            completion_date="2026-01-30 22:10:58",
            category=CategoryEnum.alimento,
            description="Stress test",
            source=SourceEnum.efectivo_casa,
        )
        tasks.append(manager.create(i, expense))

    # Wait for all asynchronous tasks (promises) to finish
    await asyncio.gather(*tasks)

    end_time = time.perf_counter()
    duration = end_time - start_time

    # Assert: Verify data integrity and performance metrics
    print(f"\n🚀 Processed {TOTAL_MESSAGES} messages in {duration:.2f} seconds")
    print(f"⚡ Speed: {TOTAL_MESSAGES / duration:.2f} messages/second")

    count = await manager.get_total_count()
    assert count >= TOTAL_MESSAGES

    # Cleanup: Graceful shutdown
    await manager.db.shutdown()
