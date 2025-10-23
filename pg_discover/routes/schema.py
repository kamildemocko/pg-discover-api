from typing import Self
import psycopg
from cachetools import TTLCache, cached

from models.schema import Database


cache = TTLCache(maxsize=100, ttl=360)


class Schema:
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
    def get_schemas(self, database: str) -> Database:
        query = """
        SELECT table_schema as schema
        FROM information_schema.tables
        WHERE table_schema not in ('pg_catalog', 'information_schema');
        """
        assert self.connection is not None, "connection not set up"
        with self.connection.cursor() as cur:
            cur.execute(query)
            values = cur.fetchall()
        
        return Database(
            database_name=database,
            schemas=[a[0] for a in values],
        )
