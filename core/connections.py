from contextlib import contextmanager
from typing import Any

from psycopg2.pool import ThreadedConnectionPool

from core.config import get_settings

settings = get_settings()


class ConnectDB:

    def __init__(self) -> None:
        self.conn_pg_pool = ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PW,
            host=settings.SERVICE_POSTGRES_HOST,
            port=settings.SERVICE_POSTGRES_PORT,
        )

    @contextmanager
    def get_pg_conn(self) -> Any:
        conn = self.conn_pg_pool.getconn()
        try:
            yield conn
        finally:
            self.put_pg_conn(conn)

    def put_pg_conn(self, conn: Any) -> None:
        self.conn_pg_pool.putconn(conn=conn)

    def close_all_pg_conn(self):
        self.conn_pg_pool.closeall()
