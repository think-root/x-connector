import requests
from requests_oauthlib import OAuth1
import os
from dotenv import load_dotenv

load_dotenv()

auth = OAuth1(
    os.getenv("CONSUMER_KEY"),
    os.getenv("CONSUMER_SECRET"), 
    os.getenv("ACCESS_TOKEN"),
    os.getenv("ACCESS_TOKEN_SECRET")
)

response = requests.get(
    "https://api.twitter.com/2/users/me",
    auth=auth
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
