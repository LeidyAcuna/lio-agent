from contextlib import asynccontextmanager
from typing import AsyncIterator

import psycopg
from psycopg_pool import AsyncConnectionPool

from src.core.config import get_settings
from src.core.cursor import LoggingCursor
from src.core.exceptions import DatabaseConnectionError

settings = get_settings()


class DatabaseManager:
    """
    Manages the asynchronous connection pool for the PostgreSQL database.

    This class centralizes the database configuration, lifecycle (opening/closing),
    and provides a safe context manager for obtaining connections using a custom cursor factory.
    """

    def __init__(self) -> None:
        """
        Initializes the database connection parameters and the connection pool object.

        The pool is configured with a custom 'LoggingCursor' factory and is not opened immediately.
        """
        conn_str = f"dbname={settings.POSTGRES_DB} user={settings.POSTGRES_USER} password={settings.POSTGRES_PW} host={settings.POSTGRES_HOST} port={int(settings.POSTGRES_PORT)}"
        self.conn_pg_pool = AsyncConnectionPool(
            min_size=2,
            max_size=10,
            conninfo=conn_str,
            kwargs={"cursor_factory": LoggingCursor},
            open=False,
        )

    async def initialize(self) -> None:
        """
        Asynchronously establishes the initial connections in the pool.

        It is invoked during the application startup phase.
        """
        try:
            await self.conn_pg_pool.open()
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to open pool: {str(e)}")

    async def shutdown(self) -> None:
        """
        Asynchronously closes all active connections in the pool.

        It is invoked during the application shutdown phase to ensure a graceful exit.
        """
        await self.conn_pg_pool.close()

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[psycopg.AsyncConnection]:
        """
        Asynchronous context manager to acquire and release a database connection.

        Automatically manages the scope of the connection: it acquires one from the pool,
        yields it for use, and ensures it is returned (or committed/rolled back) upon exit.

        Yields:
            psycopg.AsyncConnection: An active database connection configured with LoggingCursor.
        """
        async with self.conn_pg_pool.connection() as conn:
            async with conn:
                yield conn
