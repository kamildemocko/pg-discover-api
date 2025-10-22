from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def custom_handler(request: Request, exc: Exception):
    status_code = exc.status_code if isinstance(exc, HTTPException) else 500
    detail = exc.detail if isinstance(exc, HTTPException) else str(exc)

    return JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "status": "error",
            "message": {"desc": detail}
        }
    )    


async def not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "status": "error",
            "message": {"desc": "Resource not found"}
        }
    )


async def not_authenticated_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=403,
        content={
            "code": 403,
            "status": "error",
            "message": {"desc": "Not authenticated"}
        }
    )
