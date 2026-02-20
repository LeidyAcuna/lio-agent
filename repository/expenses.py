import asyncio
import logging

import psycopg

from core.database import DatabaseManager
from core.exceptions.base import ConfigurationError, DatabaseError, DatabaseInsertError
from models.expense import Expense

logger = logging.getLogger(__name__)


class ExpenseRepository:
    """
    Handles persistence operations for expenses in the database.

    This repository abstracts the database details, providing a domain-centric
    interface for expense-related data operations.
    """

    def __init__(self) -> None:
        """
        Initializes the repository with a DatabaseManager instance to handle connections.
        """
        self.db = DatabaseManager()

    async def setup_schema(self) -> None:
        """
        Sets up the database structure required for the repository.

        Reads the SQL definitions from 'core/table.sql' and applies them
        asynchronously. This is invoked during application initialization.

        Raises:
            psycopg.Error: If the SQL execution fails.
            OSError: If the SQL file cannot be read.
        """
        try:

            def read_sql() -> str:
                with open("core/schema.sql", "r", encoding="utf-8") as file:
                    return file.read()

            sql_script = await asyncio.to_thread(read_sql)

            async with self.db.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql_script)

            logger.info("Database schema initialized successfully.")

        except OSError as e:
            raise ConfigurationError(f"SQL file core/table.sql not found: {e}")
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
