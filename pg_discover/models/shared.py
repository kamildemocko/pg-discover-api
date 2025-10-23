from typing import Any

from pydantic import BaseModel


class Schemas(BaseModel):
    database_name: str
    schemas: list[str]


class Tables(BaseModel):
    database_name: str
    schema_name: str
    tables: list[str]


class TableColumn(BaseModel):
    column_name: str
    data_type: str
    char_max_len: int | None
    is_nullable: bool
    default: str


class Table(BaseModel):
    database_name: str
    schema_name: str
    table_name: str
    columns: list[TableColumn]


class TableSample(BaseModel):
    database_name: str
    schema_name: str
    table_name: str
    sample_data: list[dict[str, Any]]


class TableConstraint(BaseModel):
    constraint_name: str
    constraint_type: str
    column_name: str


class TableConstraints(BaseModel):
    database_name: str
    schema_name: str
    table_name: str
    constraints: list[TableConstraint]

