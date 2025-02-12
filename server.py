import uvicorn
import asyncio
from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
from datetime import datetime

from config import SERVER_CONFIG
from logger import logger
from middleware import APIKeyMiddleware
from twitter_client import TwitterClient

app = FastAPI()
app.add_middleware(APIKeyMiddleware)
twitter_client = TwitterClient()


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
        result = await twitter_client.post_tweet_with_media(text, url, image_data)
    else:
        logger.info("No image in request")
        result = await twitter_client.post_tweet_with_media(text, url)

    logger.info(f"Request completed with result: {result}")
    return result


@app.post("/x/api/test/posts/create")
async def create_test_post():
    logger.info("Received test post request")
    test_text = "test"
    result = await twitter_client.post_tweet_with_media(test_text)
    logger.info(f"Test request completed with result: {result}")
    return result


if __name__ == "__main__":
    logger.info("Starting X API server...")
    uvicorn.run(app, host="0.0.0.0", port=SERVER_CONFIG["PORT"])
