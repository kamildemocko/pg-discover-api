from pydantic import BaseModel


class Schemas(BaseModel):
    database_name: str
    schemas: list[str]


class Tables(BaseModel):
    database_name: str
    schema_name: str
    tables: list[str]
