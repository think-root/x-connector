import requests
from requests_oauthlib import OAuth1
from config import TWITTER_AUTH

auth = OAuth1(
    TWITTER_AUTH["CONSUMER_KEY"],
    TWITTER_AUTH["CONSUMER_SECRET"],
    TWITTER_AUTH["ACCESS_TOKEN"],
    TWITTER_AUTH["ACCESS_TOKEN_SECRET"],
)

response = requests.get("https://api.twitter.com/2/users/me", auth=auth)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
