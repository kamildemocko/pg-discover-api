from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    user: str
    password: str
    host: str
    port: int = 5432
    database: str = "postgres"
