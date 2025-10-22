from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

from discoverer.discoverer import Discoverer
from discoverer.models import Collection


app = FastAPI()


class DatabaseConfig(BaseModel):
    user: str
    password: str
    host: str
    port: int = 5432
    database: str = "postgres"


@app.get("/discover/{schema}")
def discover(schema: str, config: DatabaseConfig) -> list[Collection]:
    try:
        db = Discoverer(**config.model_dump())
        return db.discover_tables()

    except (TimeoutError, ConnectionError) as err:
        raise HTTPException(
            status_code=400,
            detail=str(err)
        )


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
