import time
import hmac
import hashlib
import base64
import requests
import logging
import os
import uvicorn

from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import JSONResponse
from requests_oauthlib import OAuth1
from typing import Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(status_code=401, content={"error": "API Key missing"})

        if api_key != os.getenv("SERVER_API_KEY"):
            return JSONResponse(status_code=403, content={"error": "Invalid API Key"})

        response = await call_next(request)
        return response


app = FastAPI()
app.add_middleware(APIKeyMiddleware)

load_dotenv()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")


async def post_tweet_with_media(text: str, url: Optional[str] = None, image_data: bytes = None):
    auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)

    if image_data:
        logger.info("Uploading media to Twitter")
        media_url = "https://upload.twitter.com/1.1/media/upload.json"
        files = {"media": image_data}
        media_response = requests.post(media_url, files=files, auth=auth)
        media_id = media_response.json()["media_id_string"]
        logger.info(f"Media uploaded successfully with ID: {media_id}")

        tweet_url = "https://api.twitter.com/2/tweets"
        data = {"text": text, "media": {"media_ids": [media_id]}}
    else:
        tweet_url = "https://api.twitter.com/2/tweets"
        data = {"text": text}

    try:
        logger.info(f"Posting main tweet: {text[:50]}...")
        response = requests.post(
            tweet_url, json=data, auth=auth, headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        main_tweet = response.json()
        logger.info("Main tweet posted successfully")

        if url:
            reply_data = {
                "text": url,
                "reply": {"in_reply_to_tweet_id": main_tweet["data"]["id"]}
            }
            logger.info(f"Posting URL as reply: {url}")
            reply_response = requests.post(
                tweet_url, json=reply_data, auth=auth, headers={"Content-Type": "application/json"}
            )
            reply_response.raise_for_status()
            logger.info("Reply with URL posted successfully")
            return {"main_tweet": main_tweet, "reply_tweet": reply_response.json()}

        return main_tweet
    except requests.exceptions.RequestException as error:
        logger.error(f"Error posting tweet: {error}")
        return {"error": str(error)}


@app.post("/x/api/posts/create")
async def create_post(
    text: str = Form(...),
    url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Received post request at {request_time}")
    logger.info(f"Text content: {text[:50]}...")
    if url:
        logger.info(f"URL included: {url}")

    if image:
        logger.info(f"Image included in request: {image.filename}")
        image_data = await image.read()
        result = await post_tweet_with_media(text, url, image_data)
    else:
        logger.info("No image in request")
        result = await post_tweet_with_media(text, url)

    logger.info(f"Request completed with result: {result}")
    return result


if __name__ == "__main__":
    logger.info("Starting X API server...")
    port = int(os.getenv("SERVER_PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
