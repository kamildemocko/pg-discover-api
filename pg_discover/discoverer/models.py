from typing import Literal

from pydantic import BaseModel, Field


class TableColumn(BaseModel):
    name: str
    data_type: str
    char_max_len: int | None
    is_nullable: bool
    default: str


class Table(BaseModel):
    name: str
    table_type: Literal["view", "table", "unknown"]
    columns: list[TableColumn]


class Schema(BaseModel):
    name: str
    tables: list[Table]


class Collection(BaseModel):
    name: str
    schemas: list[Schema]


class _SchemasTables(BaseModel):
    catalog: str
    schema_: str = Field(alias="schema")
    table: str
    table_type: str
