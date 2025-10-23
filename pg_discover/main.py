from fastapi import FastAPI, HTTPException
import uvicorn

from models.main import DatabaseConfig
from routes.explore import Explore
from models.explore import Collection
from exception_handlers import custom_handler
from exception_handlers import not_found_handler
from exception_handlers import not_authenticated_handler


app = FastAPI()

app.add_exception_handler(HTTPException, custom_handler)
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(403, not_authenticated_handler)

@app.get("/explore")
def explore(config: DatabaseConfig) -> list[Collection]:
    try:
        with Explore(**config.model_dump()) as explorer:
            return explorer.explore_tables()

    except (TimeoutError, ConnectionError) as err:
        raise HTTPException(
            status_code=400,
            detail=err
        )


@app.get("/schema/list")
def schema_list(config: DatabaseConfig) -> list[Collection]:
    ...


@app.get("/table/{schema}/list")
def table_list(config: DatabaseConfig) -> list[Collection]:
    ...


@app.get("/table/{schema}/{table}")
def table_detail(schema: str, config: DatabaseConfig) -> list[Collection]:
    ...


@app.get("/table/{schema}/{table}/sample")
def table_example(schema: str, config: DatabaseConfig) -> list[Collection]:
    ...


@app.get("/stats/{schema}")
def stats(schema: str, config: DatabaseConfig) -> list[Collection]:
    ...


if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, reload=True)
