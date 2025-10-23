from typing import Literal, Callable, Self

import psycopg
from psycopg.rows import class_row
from psycopg.cursor import Cursor
import polars as pl
from cachetools import TTLCache, cached

from models.explore import ExploreDatabase, Schema, Table, TableColumn, _SchemasTables


cache = TTLCache(maxsize=100, ttl=360)


class Explore:
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
    def explore_tables(self) -> list[ExploreDatabase]:
        query = """
        SELECT table_catalog as catalog, table_schema as schema, table_name as table, table_type
        FROM information_schema.tables
        WHERE table_schema not in ('pg_catalog', 'information_schema');
        """
        assert self.connection is not None, "connection not set up"
        with self.connection.cursor(row_factory=class_row(_SchemasTables)) as cur:
            cur.execute(query)
            schemas_tables = cur.fetchall()

        df = pl.from_records(schemas_tables)
        df = df.with_columns(
            pl.col("table_type")
            .str.replace_all("BASE TABLE", "table")
            .str.replace_all("VIEW", "view")
        )

        collections = []
        all_catalogs = df["catalog"].unique().sort().to_list()
        for cat in all_catalogs:
            fil_cat = df.filter(pl.col("catalog") == cat)

            schemas = []
            all_schemas = fil_cat["schema_"].unique().sort().to_list()
            for sch in all_schemas:
                fil_sch = fil_cat.filter(pl.col("schema_") == sch)

                tables = []
                for row in fil_sch.iter_rows(named=True):
                    table_desc = self.explore_table_columns(
                        sch, 
                        row["table"],
                        row["table_type"]
                    )
                    table = Table(
                        table_name=row["table"],
                        table_type=row["table_type"],
                        columns=table_desc,
                    )
                    tables.append(table)

                schemas.append(Schema(schema_name=sch, tables=tables))
            
            collections.append(ExploreDatabase(database_name=cat, schemas=schemas))

        return collections
    
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

    def explore_table_columns(
            self, schema: str, table: str, table_type: Literal["view", "table"]
    ) -> list[TableColumn]:
        query = """
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_schema = %s AND table_name = %s;
        """
        assert self.connection is not None, "connection not set up"
        with self.connection.cursor(row_factory=self._table_col_row_factory) as cur:
            cur.execute(query, (schema, table))
            table_columns: list[TableColumn] = cur.fetchall()

        return table_columns


if __name__ == "__main__":
    di = Explore(host="192.168.0.12", port=5432, database="postgres", user="postgres", password="")
    collections = di.explore_tables()
    print(collections)
