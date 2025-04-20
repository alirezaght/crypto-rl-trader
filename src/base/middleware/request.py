from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar
from typing import Optional

_request_context: ContextVar[Optional[Request]] = ContextVar("request_context", default=None)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = _request_context.set(request)
        try:
            response = await call_next(request)
        finally:
            _request_context.reset(token)
        return response
    
def get_current_request() -> Optional[Request]:
    return _request_context.get()