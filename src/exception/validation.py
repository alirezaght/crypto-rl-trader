from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI
import logging
import json

logger = logging.getLogger("Validation")

def register_validation_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error at {request.url}")
        logger.error(json.dumps(exc.errors(), indent=2))
        try:
            body = await request.body()
            logger.error(f"📦 Request body: {body.decode()}")
        except Exception:
            logger.error("Could not read request body.")

        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )
        
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )