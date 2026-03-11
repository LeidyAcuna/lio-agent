import asyncio
import logging

import psycopg

from src.core.database import DatabaseManager
from src.core.exceptions import ConfigurationError, DatabaseError, DatabaseInsertError
from src.models.expense import Expense

logger = logging.getLogger(__name__)


class ExpenseRepository:
    """
    Handles persistence operations for expenses in the database.

    This repository abstracts the database details, providing a domain-centric
    interface for expense-related data operations.
    """

    def __init__(self, db: DatabaseManager) -> None:
        """
        Initializes the repository with a shared DatabaseManager instance.

        Args:
            db (DatabaseManager): The shared database manager.
        """
        self.db = db

    async def setup_schema(self) -> None:
        """
        Sets up the database structure required for the repository.

        Reads the SQL definitions from 'src/core/schema_expenses.sql' and applies them
        asynchronously. This is invoked during application initialization.

        Raises:
            psycopg.Error: If the SQL execution fails.
            OSError: If the SQL file cannot be read.
        """
        try:

            def read_sql() -> str:
                with open(
                    "src/core/schema_expenses.sql", "r", encoding="utf-8"
                ) as file:
                    return file.read()

            sql_script = await asyncio.to_thread(read_sql)

            async with self.db.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql_script)

            logger.info("Database schema initialized successfully.")

        except OSError as e:
            raise ConfigurationError(
                f"SQL file core/schema_expenses.sql not found: {e}"
            )
        except psycopg.Error as e:
            raise DatabaseError(f"Failed to execute schema initialization: {e}")

    async def create(self, user_id: int, expense: Expense) -> None:
        """
        Persists a new expense record into the database.

        Args:
            user_id (int): The Telegram user ID associated with the expense.
            expense (Expense): The structured expense data model to be saved.

        Raises:
            DatabaseInsertError: A custom exception wrapped around database failures
                                during insertion to provide domain-specific context.
        """
        try:
            async with self.db.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """INSERT INTO expenses (user_id, completion_date, category, source, description, total)
                        values (%s, %s, %s, %s, %s, %s)""",
                        (
                            user_id,
                            expense.completion_date,
                            expense.category.value,
                            expense.source.value,
                            expense.description,
                            expense.total,
                        ),
                    )
                    logger.info("New row was inserted successfully!")

        except psycopg.Error as error:
            logger.error(f"Failed to insert a new row in table, {error}")
            raise DatabaseInsertError(f"Failed to insert a new row in table {user_id}")

    async def get_total_count(self) -> int:
        """
        Returns the total number of records in the expenses table.

        Returns:
            int: The total number of records in the expenses table.

        Raises:
            DatabaseError: A custom exception wrapped around database failures
                                during insertion to provide domain-specific context.
        """
        try:
            async with self.db.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT COUNT(*) FROM expenses")
                    result = await cur.fetchone()
                    return result[0] if result else 0
        except psycopg.Error as error:
            logger.error(f"Failed to get total count: {error}")
            raise DatabaseError(f"Failed to get total count: {error}")
