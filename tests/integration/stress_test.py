import asyncio
import time

import pytest

from src.models.expense import CategoryEnum, Expense, SourceEnum
from src.repository.expenses import ExpenseRepository


@pytest.mark.asyncio
async def test_stress_db_insertion():
    TOTAL_MESSAGES = 1000
    manager = ExpenseRepository()
    await manager.db.initialize()
    await manager.setup_schema()

    # 1. Clean DB test
    async with manager.db.get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM expenses")

    tasks = []
    start_time = time.perf_counter()

    # 2. Insert 1000 messages
    for i in range(TOTAL_MESSAGES):
        expense = Expense(
            total=100.0,
            completion_date="2026-01-30 22:10:58",
            category=CategoryEnum.alimento,
            description="Stress test",
            source=SourceEnum.efectivo_casa,
        )
        tasks.append(manager.create(i, expense))

    # Wait for all promises to finish
    await asyncio.gather(*tasks)

    end_time = time.perf_counter()
    duration = end_time - start_time

    # 3. Assert: Robustness checks
    print(f"\n🚀 Processed {TOTAL_MESSAGES} messages in {duration:.2f} seconds")
    print(f"⚡ Speed: {TOTAL_MESSAGES / duration:.2f} messages/second")

    # Verify that they are actually in the DB
    count = await manager.get_total_count()
    assert count >= TOTAL_MESSAGES

    await manager.db.shutdown()
