import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_AUTH = {
    "CONSUMER_KEY": os.getenv("CONSUMER_KEY"),
    "CONSUMER_SECRET": os.getenv("CONSUMER_SECRET"),
    "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN"),
    "ACCESS_TOKEN_SECRET": os.getenv("ACCESS_TOKEN_SECRET"),
}

SERVER_CONFIG = {
    "API_KEY": os.getenv("SERVER_API_KEY"),
    "PORT": int(os.getenv("SERVER_PORT", 8080)),
}

TWITTER_API = {
    "TWEET_URL": "https://api.x.com/2/tweets",
    "MEDIA_UPLOAD_URL": "https://upload.twitter.com/1.1/media/upload.json",
    "MAX_TWEET_LENGTH": 270,
    "DELAY_BETWEEN_REQUESTS": 5,
}
