import asyncio
import requests
from requests_oauthlib import OAuth1
from typing import Optional, List
from config import TWITTER_AUTH, TWITTER_API
from logger import logger
import math

class TwitterClient:
    def __init__(self):
        self.auth = OAuth1(
            TWITTER_AUTH["CONSUMER_KEY"],
            TWITTER_AUTH["CONSUMER_SECRET"],
            TWITTER_AUTH["ACCESS_TOKEN"],
            TWITTER_AUTH["ACCESS_TOKEN_SECRET"],
        )

    async def make_twitter_request(self, url: str, data: dict, headers: dict):
        max_retries = 3
        retry_delay = 30

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=data, auth=self.auth, headers=headers)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                logger.error(f"Twitter API error: {e.response.text}")
                if attempt < max_retries - 1:
                    logger.info(
                        f"Retrying request in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(
                        f"Retrying request in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    raise
        return None

    @staticmethod
    def split_text_into_parts(text: str) -> List[str]:
        max_length = TWITTER_API["MAX_TWEET_LENGTH"]
        if len(text) <= max_length:
            return [text]
        total_parts = math.ceil(len(text) / max_length)
        target_length = math.ceil(len(text) / total_parts)
        parts = []
        while text:
            if len(text) <= max_length:
                parts.append(text)
                break
            start = max(target_length - 20, 0)
            end = min(target_length + 20, len(text))
            split_index = text.rfind(" ", start, end)
            if split_index == -1:
                split_index = text.rfind(" ", 0, max_length)
                if split_index == -1:
                    split_index = max_length
            parts.append(text[:split_index].strip())
            text = text[split_index:].strip()
        return parts

    async def post_tweet_with_media(
        self, text: str, url: Optional[str] = None, image_data: bytes = None
    ):
        tweets_data = []
        text_parts = self.split_text_into_parts(text)
        total_parts = len(text_parts)

        try:
            first_text = text_parts[0]
            if total_parts > 1:
                first_text = f"🧵 0/{total_parts-1} {first_text}"

            if image_data:
                logger.info("Uploading media to Twitter")
                files = {"media": image_data}
                media_response = requests.post(
                    TWITTER_API["MEDIA_UPLOAD_URL"], files=files, auth=self.auth
                )
                media_response.raise_for_status()
                media_id = media_response.json()["media_id_string"]
                logger.info(f"Media uploaded successfully with ID: {media_id}")
                data = {"text": first_text, "media": {"media_ids": [media_id]}}
            else:
                data = {"text": first_text}

            logger.info(f"Posting first tweet: {first_text[:50]}...")
            response = await self.make_twitter_request(
                TWITTER_API["TWEET_URL"], data, {"Content-Type": "application/json"}
            )
            previous_tweet_id = response.json()["data"]["id"]
            tweets_data.append(response.json())

            for i, part in enumerate(text_parts[1:], 1):
                await asyncio.sleep(TWITTER_API["DELAY_BETWEEN_REQUESTS"])
                text_with_counter = f"🧵 {i}/{total_parts-1} {part}"
                reply_data = {
                    "text": text_with_counter,
                    "reply": {"in_reply_to_tweet_id": previous_tweet_id},
                }
                logger.info(f"Posting part {i}: {text_with_counter[:50]}...")
                reply_response = await self.make_twitter_request(
                    TWITTER_API["TWEET_URL"], reply_data, {"Content-Type": "application/json"}
                )
                tweets_data.append(reply_response.json())
                previous_tweet_id = reply_response.json()["data"]["id"]

            if url:
                await asyncio.sleep(TWITTER_API["DELAY_BETWEEN_REQUESTS"])
                reply_data = {"text": url, "reply": {"in_reply_to_tweet_id": previous_tweet_id}}
                logger.info(f"Posting URL as final reply: {url}")
                reply_response = await self.make_twitter_request(
                    TWITTER_API["TWEET_URL"], reply_data, {"Content-Type": "application/json"}
                )
                tweets_data.append(reply_response.json())

            return {"tweets": tweets_data}
        except requests.exceptions.RequestException as error:
            logger.error(f"Error posting tweet: {error}")
            return {"error": str(error)}
