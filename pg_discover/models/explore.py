from typing import Literal

from pydantic import BaseModel, Field


class TableColumn(BaseModel):
    column_name: str
    data_type: str
    char_max_len: int | None
    is_nullable: bool
    default: str


class Table(BaseModel):
    table_name: str
    table_type: Literal["view", "table", "unknown"]
    columns: list[TableColumn]


class Schema(BaseModel):
    schema_name: str
    tables: list[Table]


class ExploreDatabase(BaseModel):
    database_name: str
    schemas: list[Schema]


class _SchemasTables(BaseModel):
    catalog: str
    schema_: str = Field(alias="schema")
    table: str
    table_type: str
