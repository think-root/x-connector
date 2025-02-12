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
        mid = len(text) // 2
        split_index = text.rfind(" ", 0, mid)
        if split_index == -1:
            split_index = mid
        part1 = text[:split_index].strip()
        part2 = text[split_index:].strip()
        return [part1, part2]

    async def post_tweet_with_media(
        self, text: str, url: Optional[str] = None, image_data: bytes = None
    ):
        tweets_data = []
        text_parts = self.split_text_into_two(text)

        try:
            if image_data:
                logger.info("Uploading media to Twitter")
                files = {"media": image_data}
                media_response = requests.post(
                    TWITTER_API["MEDIA_UPLOAD_URL"], files=files, auth=self.auth
                )
                media_response.raise_for_status()
                media_id = media_response.json()["media_id_string"]
                logger.info(f"Media uploaded successfully with ID: {media_id}")
                data = {"text": text_parts[0], "media": {"media_ids": [media_id]}}
            else:
                data = {"text": text_parts[0]}

            logger.info(f"Posting first tweet: {text_parts[0][:50]}...")
            response = await self.make_twitter_request(
                TWITTER_API["TWEET_URL"], data, {"Content-Type": "application/json"}
            )
            previous_tweet_id = response.json()["data"]["id"]
            tweets_data.append(response.json())

            if len(text_parts) > 1:
                await asyncio.sleep(TWITTER_API["DELAY_BETWEEN_REQUESTS"])
                reply_data = {
                    "text": text_parts[1],
                    "reply": {"in_reply_to_tweet_id": previous_tweet_id},
                }
                logger.info(f"Posting second tweet: {text_parts[1][:50]}...")
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
