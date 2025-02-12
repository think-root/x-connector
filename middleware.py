from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from config import SERVER_CONFIG


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(status_code=401, content={"error": "API Key missing"})

        if api_key != SERVER_CONFIG["API_KEY"]:
            return JSONResponse(status_code=403, content={"error": "Invalid API Key"})

        response = await call_next(request)
        return response
