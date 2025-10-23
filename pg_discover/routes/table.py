from typing import Self, Callable
import psycopg
from psycopg.cursor import Cursor
from psycopg.sql import SQL
from cachetools import TTLCache, cached

from models.shared import Tables
from models.shared import Table
from models.shared import TableColumn
from models.shared import TableSample


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

    @staticmethod
    def _table_col_row_factory(cursor: Cursor) -> Callable:
        def make_table(values):
            return TableColumn(
                column_name=values[0],
                data_type=values[1],
                char_max_len=values[2],
                is_nullable=values[3] == "YES",
                default=values[4] or "",
            )
        
        return make_table

    @cached(cache)
    def get_columns(self, database: str, schema: str, table: str) -> Table:
        query = """
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_catalog = %s AND table_schema = %s AND table_name = %s;
        """
        assert self.connection is not None, "connection not set up"
        with self.connection.cursor(row_factory=self._table_col_row_factory) as cur:
            cur.execute(query, (database, schema, table))
            values = cur.fetchall()
        
        return Table(
            database_name=database,
            schema_name=schema,
            table_name=table,
            columns=values
        )

    @cached(cache)
    def get_sample(self, database: str, schema: str, table: str) -> TableSample:
        query = f"""
        SELECT *
        FROM {schema}.{table}
        ORDER BY RANDOM()
        LIMIT 10;
        """
        assert self.connection is not None, "connection not set up"
        with self.connection.cursor() as cur:
            cur.execute(query)  #type: ignore
            header = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()

            data = []
            for row in rows:
                dct = {}
                for h, v in zip(header, row):
                    v = v if v is not None and not isinstance(v, (str, int, float, bool)) else str(v)
                    dct[h] = v
                data.append(dct)
            
        return TableSample(
            database_name=database,
            schema_name=schema,
            table_name=table,
            sample_data=data,
        )

