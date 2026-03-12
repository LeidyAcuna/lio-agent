import asyncio
import logging

import psycopg

from src.core.database import DatabaseManager
from src.core.exceptions import ConfigurationError, DatabaseError, DatabaseInsertError
from src.models.audit_log import AuditLog, AuditLogInDB

logger = logging.getLogger(__name__)


class AuditLogsRepository:
    """
    Handles persistence operations for audit logs in the database.

    This repository abstracts the database details, providing a domain-centric
    interface for audit logs-related data operations.
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

        Reads the SQL definitions from 'src/core/schema_audit_logs.sql' and applies them
        asynchronously. This is invoked during application initialization.

        Raises:
            psycopg.Error: If the SQL execution fails.
            OSError: If the SQL file cannot be read.
        """
        try:

            def read_sql() -> str:
                with open(
                    "src/core/schema_audit_logs.sql", "r", encoding="utf-8"
                ) as file:
                    return file.read()

            sql_script = await asyncio.to_thread(read_sql)

            async with self.db.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(sql_script)

            logger.info("Database Audit Logs schema initialized successfully.")

        except OSError as e:
            raise ConfigurationError(
                f"SQL file core/schema_audit_logs.sql not found: {e}"
            )
        except psycopg.Error as e:
            raise DatabaseError(f"Failed to execute schema initialization: {e}")

    async def create(self, audit_log: AuditLog) -> None:
        """
        Persists a new audit log record into the database.

        Args:
            audit_log (AuditLog): The structured audit log data model to be saved.

        Raises:
            DatabaseInsertError: A custom exception wrapped around database failures
                                during insertion to provide domain-specific context.
        """
        try:
            async with self.db.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """INSERT INTO audit_logs (user_id, fullname, username, chat_id, message_text, message_date)
                        values (%s, %s, %s, %s, %s, %s)""",
                        (
                            audit_log.user_id,
                            audit_log.fullname,
                            audit_log.username,
                            audit_log.chat_id,
                            audit_log.message_text,
                            audit_log.message_date,
                        ),
                    )
                    logger.info("New audit log was inserted successfully!")

        except psycopg.Error as error:
            logger.error(f"Failed to insert a new audit log in table, {error}")
            raise DatabaseInsertError(
                f"Failed to insert a new audit log in table {audit_log.user_id}"
            )

    async def get_last_audit_log(self) -> AuditLogInDB:
        """
        Returns the last audit log record in the audit_logs table.

        Returns:
            AuditLog: The last audit log record in the audit_logs table.

        Raises:
            DatabaseError: A custom exception wrapped around database failures
                                during insertion to provide domain-specific context.
        """
        try:
            async with self.db.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT * FROM public.audit_logs ORDER BY created_at desc limit 1"
                    )
                    result = await cur.fetchone()
                    audit_log = AuditLogInDB(
                        id=result[0],
                        user_id=result[1],
                        fullname=result[2],
                        username=result[3],
                        chat_id=result[4],
                        message_text=result[5],
                        message_date=result[6],
                        created_at=result[7],
                    )
                    return audit_log
        except psycopg.Error as error:
            logger.error(f"Failed to get last audit log: {error}")
            raise DatabaseError(f"Failed to get last audit log: {error}")
