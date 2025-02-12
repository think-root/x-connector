import asyncio
import requests
from requests_oauthlib import OAuth1
from typing import Optional, List
from config import TWITTER_AUTH, TWITTER_API
from logger import logger


class TwitterClient:
    def __init__(self):
        self.auth = OAuth1(
            TWITTER_AUTH["CONSUMER_KEY"],
            TWITTER_AUTH["CONSUMER_SECRET"],
            TWITTER_AUTH["ACCESS_TOKEN"],
            TWITTER_AUTH["ACCESS_TOKEN_SECRET"],
        )

    async def make_twitter_request(self, url: str, data: dict, headers: dict):
        try:
            response = requests.post(url, json=data, auth=self.auth, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            logger.error(f"Twitter API error: {e.response.text}")
            raise

    def split_text_into_two(self, text: str) -> List[str]:
        if len(text) <= TWITTER_API["MAX_TWEET_LENGTH"]:
            return [text]

        total_length = len(text)
        target_length = total_length // 2

        max_part_length = TWITTER_API["MAX_TWEET_LENGTH"] - 6
        target_length = min(target_length, max_part_length)

        parts = []
        remaining_text = text

        while remaining_text:
            if len(remaining_text) <= max_part_length:
                parts.append(remaining_text)
                break

            split_index = remaining_text.rfind(" ", target_length - 20, target_length + 20)
            if split_index == -1:
                split_index = target_length

            parts.append(remaining_text[:split_index].strip())
            remaining_text = remaining_text[split_index:].strip()

        return parts

    async def post_tweet_with_media(
        self, text: str, url: Optional[str] = None, image_data: bytes = None
    ):
        tweets_data = []
        text_parts = self.split_text_into_two(text)
        total_parts = len(text_parts)
        previous_tweet_id = None

        try:
            first_text = text_parts[0]
            if total_parts > 1:
                first_text = f"🧵 1/{total_parts} {first_text}"

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

            for i, part in enumerate(text_parts[1:], 2):
                await asyncio.sleep(TWITTER_API["DELAY_BETWEEN_REQUESTS"])
                text_with_counter = f"🧵 {i}/{total_parts} {part}"
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
