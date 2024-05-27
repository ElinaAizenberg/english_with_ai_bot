import logging
import psycopg2.pool

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Creates a pool with maximum connections for a database."""
    def __init__(self, max_connections,  **kwargs):
        self.pool = psycopg2.pool.SimpleConnectionPool(minconn=1,
                                                       maxconn=max_connections,  **kwargs)

    def acquire(self):
        """Acquire a connection from the pool."""
        try:
            return self.pool.getconn()
        except Exception:
            raise TimeoutError("Timeout: No available connections in the pool")

    def release(self, connection):
        """Release a connection back to the pool."""
        self.pool.putconn(connection)

