from pydantic import BaseModel


class Database(BaseModel):
    database_name: str
    schemas: list[str]
