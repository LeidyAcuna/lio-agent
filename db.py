import psycopg2
import psycopg2.extensions
import logging
from config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('db_init')

class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger.info(self.mogrify(sql, args))
        try:
            psycopg2.extensions.cursor.execute(self, sql, args)
        except Exception as error:
            logger.error(f"SQL Error: {error}")
            raise

def init_db():
    settings = get_settings()
    try:
        conn = psycopg2.connect(
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER, 
            password=settings.POSTGRES_PW,
            host=settings.SERVICE_POSTGRES_HOST,
            port=settings.SERVICE_POSTGRES_PORT
            )
        cur = conn.cursor(cursor_factory=LoggingCursor)
        with open("table.sql", "r") as file_sql:
            sql_script = file_sql.read()
            cur.execute(sql_script)

        conn.commit()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to connect or initialize DB: {e}")
        raise