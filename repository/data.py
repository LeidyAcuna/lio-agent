import logging

import psycopg2

from core.connections import ConnectDB
from core.cursor import LoggingCursor
from core.exceptions.base import DatabaseInsertError
from models.expense import Expense

logging.basicConfig(level=logging.INFO)  # TODO: REVISAR - loop.run_in_executor
logger = logging.getLogger("db_init")


class ManagerDB:

    def __init__(self) -> None:
        self.db = ConnectDB()

    def init_db(self) -> None:
        try:
            with self.db.get_pg_conn() as conn:
                with conn.cursor(cursor_factory=LoggingCursor) as cur:
                    with open("core/table.sql", "r") as file_sql:
                        sql_script = file_sql.read()
                        cur.execute(sql_script)

                    conn.commit()
                    logger.info("Database initialized successfully.")
        except psycopg2.Error as error:
            logger.error(f"Failed to connect or initialize DB: {error}")
            raise error

    def insert_row_in_db(self, user_id: int, object: Expense) -> None:
        try:
            with self.db.get_pg_conn() as conn:
                with conn.cursor(cursor_factory=LoggingCursor) as cur:
                    cur.execute(
                        """INSERT INTO expenses (user_id, completion_date, category, source, description, total)
                        values (%s, %s, %s, %s, %s, %s)""",
                        (
                            user_id,
                            object.completion_date,
                            object.category.value,
                            object.source.value,
                            object.description,
                            object.total,
                        ),
                    )
                    conn.commit()
                    logger.info("New row was inserted successfully!")

        except psycopg2.Error as error:
            logger.error(f"Failed to insert a new row in table, {error}")
            raise DatabaseInsertError(f"Failed to insert a new row in table {user_id}")
