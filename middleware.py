from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from config import SERVER_CONFIG

class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str = SERVER_CONFIG["API_KEY"]):
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        if request.headers.get("X-API-Key") != self.api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key"
            )
        return await call_next(request)

        if api_key != SERVER_CONFIG["API_KEY"]:
            return JSONResponse(status_code=403, content={"error": "Invalid API Key"})

        response = await call_next(request)
        return response
