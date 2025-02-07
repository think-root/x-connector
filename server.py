import asyncio
import os
from twikit import Client
from fastapi import FastAPI, Body, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.responses import Response
import json

load_dotenv()
USERNAME = os.getenv("TWITTER_USERNAME")
EMAIL = os.getenv("TWITTER_EMAIL")
PASSWORD = os.getenv("TWITTER_PASSWORD")
API_KEY = os.getenv("API_KEY", "ABC")
PORT = int(os.getenv("PORT", 9007))

app = FastAPI()
client = Client("uk-UA")

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != API_KEY:
            return Response(
                status_code=403,
                content=json.dumps({"detail": "Invalid API key"}),
                media_type="application/json"
            )
        return await call_next(request)

app.add_middleware(APIKeyMiddleware)


class TweetRequest(BaseModel):
    text: str


@app.on_event("startup")
async def startup_event():
    if os.path.exists("cookies.json"):
        client.load_cookies("cookies.json")
    else:
        await client.login(
            auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD, cookies_file="cookies.json"
        )
        await client.save_cookies("cookies.json")


from fastapi import File, UploadFile
from typing import List
import tempfile

class TweetRequest(BaseModel):
    text: str

@app.post("/x/posts/create")
async def create_post(
    text: str = Body(...),
    files: List[UploadFile] = File(...)
):
    media_ids = []
    
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            
            media_id = await client.upload_media(temp_file.name)
            media_ids.append(media_id)
            
            os.unlink(temp_file.name)

    await client.create_tweet(
        text=text,
        media_ids=media_ids
    )
    
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)


