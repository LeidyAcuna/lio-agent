import logging
from psycopg2.extensions import cursor


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('db_init')


class LoggingCursor(cursor):

    def execute(self, sql, args=None):
        logger.info(self.mogrify(sql, args))
        try:
            cursor.execute(self, sql, args)
        except Exception as error:
            logger.error(f"SQL Error: {error}")
            raise