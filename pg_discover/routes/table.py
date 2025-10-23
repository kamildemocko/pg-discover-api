from typing import Self
import psycopg
from cachetools import TTLCache, cached

from models.shared import Tables


cache = TTLCache(maxsize=100, ttl=360)


class TableRoute:
    def __init__(self, host: str, port: int, database: str, user: str, password: str, connect_timeout: int = 10) -> None:
        self.dsn = f"host={host} port={port} dbname={database} user={user} password={password} connect_timeout={connect_timeout}"
        self.connection: psycopg.Connection | None = None
    
    def __enter__(self) -> Self:
        try:
            self.connection = psycopg.connect(self.dsn)

        except psycopg.errors.ConnectionTimeout as ter:
            raise TimeoutError("error connection timeout") from ter

        except psycopg.OperationalError as oer:
            raise ConnectionError("error connecting") from oer
        
        return self
    
    def __exit__(self, *args) -> None:
        if self.connection:
            self.connection.close()

    @cached(cache)
    def get_tables(self, database: str, schema: str) -> Tables:
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema not in ('pg_catalog', 'information_schema')
        and table_catalog = %s and table_schema = %s;
        """
        assert self.connection is not None, "connection not set up"
        with self.connection.cursor() as cur:
            cur.execute(query, (database, schema))
            values = cur.fetchall()
        
        return Tables(
            database_name=database,
            schema_name=schema,
            tables=[a[0] for a in values],
        )
