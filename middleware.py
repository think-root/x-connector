from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from config import SERVER_CONFIG

class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str = SERVER_CONFIG["API_KEY"]):
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/x", "/x/"]:
            return await call_next(request)

        if request.headers.get("X-API-Key") != self.api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key"}
            )
        response = await call_next(request)
        return response
