# pg-discover

A PostgreSQL database discovery tool that provides a REST API to explore database schemas, tables, and columns.

## Features

- Discover all tables and views in a PostgreSQL database
- Retrieve detailed column information including data types and constraints
- REST API interface for easy integration
- Excludes system schemas (`pg_catalog`, `information_schema`)

## Installation

```bash
git clone https://github.com/kamildemocko/pg-discover-api.git
cd pg-discover-api
uv sync
```

## Usage

### As a REST API

Start the server:

```bash
uv run pg-discover
```

The API will be available at `http://localhost:8080`

### API Endpoint

```
GET /docs
```

See Swagger documentation

```
GET /discover/{schema}
```

Send a POST request with database configuration:

```json
{
    "user": "postgres",
    "password": "your_password",
    "host": "localhost",
    "port": 5432,
    "database": "postgres"
}
```

## Dependencies

- FastAPI
- Polars
- psycopg[binary]
- Pydantic
- uvicorn
