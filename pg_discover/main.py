from fastapi import FastAPI, HTTPException
import uvicorn

from models.main import DatabaseConfig
from models.explore import ExploreDatabase
from models.shared import Schemas
from models.shared import Tables
from models.shared import Table
from routes.explore import ExploreRoute
from routes.schema import SchemaRoute
from routes.table import TableRoute
from exception_handlers import custom_handler
from exception_handlers import not_found_handler
from exception_handlers import not_authenticated_handler


app = FastAPI()

app.add_exception_handler(HTTPException, custom_handler)
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(403, not_authenticated_handler)


@app.get("/explore")
def explore(config: DatabaseConfig) -> list[ExploreDatabase]:
    try:
        with ExploreRoute(**config.model_dump()) as explorer:
            return explorer.explore_tables()

    except (TimeoutError, ConnectionError) as err:
        raise HTTPException(
            status_code=400,
            detail=err
        )


@app.get("/schema/{database}/list")
def schema_list(database: str, config: DatabaseConfig) -> Schemas:
    try:
        with SchemaRoute(**config.model_dump()) as schema:
            return schema.get_schemas(database)

    except (TimeoutError, ConnectionError) as err:
        raise HTTPException(
            status_code=400,
            detail=err
        )


@app.get("/table/{database}/{schema}/list")
def table_list(database: str, schema: str, config: DatabaseConfig) -> Tables:
    try:
        with TableRoute(**config.model_dump()) as table:
            return table.get_tables(database, schema)

    except (TimeoutError, ConnectionError) as err:
        raise HTTPException(
            status_code=400,
            detail=err
        )


@app.get("/table/{database}/{schema}/{table}")
def table_detail(database: str, schema: str, table: str, config: DatabaseConfig) -> Table:
    try:
        with TableRoute(**config.model_dump()) as tab:
            return tab.get_columns(database, schema, table)

    except (TimeoutError, ConnectionError) as err:
        raise HTTPException(
            status_code=400,
            detail=err
        )


@app.get("/table/{schema}/{table}/sample")
def table_example(schema: str, config: DatabaseConfig) -> list[Schemas]:
    ...


@app.get("/stats/{schema}")
def stats(schema: str, config: DatabaseConfig) -> list[Schemas]:
    ...


if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, reload=True)
