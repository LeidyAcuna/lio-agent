import logging
from typing import Any

import psycopg

logger = logging.getLogger(__name__)


class LoggingCursor(psycopg.AsyncClientCursor):
    """
    Custom asynchronous cursor that provides enhanced logging for SQL operations.

    Inherits from psycopg.AsyncClientCursor to leverage client-side binding,
    enabling the pre-execution formatting of SQL queries with their parameters.
    """

    async def execute(self, query: Any, params: Any = None, **kwargs: Any):
        """
        Intercepts SQL execution to log the final query and handle errors.

        This method uses 'mogrify' to combine the SQL template with its parameters
        for logging purposes before passing the execution to the parent class.

        Args:
            query (Any): The SQL query string or query object.
            params (Any, optional): Data parameters to be bound to the query.
            **kwargs: Additional keyword arguments for the psycopg execution.

        Returns:
            The result of the parent execute method.

        Raises:
            psycopg.Error: If the database execution fails, it logs the error and re-raises.
        """
        # mogrify return the final query with parameters
        sql = self.mogrify(query=query, params=params)
        logger.info(f"Executing SQL: {sql}")

        try:
            return await super().execute(query=query, params=params, **kwargs)
        except psycopg.Error as error:
            logger.error(f"SQL Error: {error}")
            raise
