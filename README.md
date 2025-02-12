# x

This repository is part of the [chappie_bot](https://github.com/Think-Root/chappie_bot) repository. If you want the bot to have Twitter integration and posts to be automatically published there as well, you need to deploy this app.  


## Description

This app provides a FastAPI-based server that integrates with the Twitter API to post tweets with optional media and URLs. It includes API key middleware for secure access and uses OAuth1 for authentication with the Twitter API.

## Features

- Post tweets with text content.
- Optionally attach media (images) to tweets.
- Optionally include a URL in the tweet as a reply.
- Secure API access using API key middleware.
- Logging for request and response tracking.

## Prerequisites

- Python 3.7 or higher
- FastAPI
- Uvicorn
- Requests
- Requests-OAuthlib
- Python-dotenv

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Think-Root/x.git
   cd x
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file in the project root with the following environment variables:**

   ```
   SERVER_API_KEY=your_server_api_key
   CONSUMER_KEY=your_twitter_consumer_key
   CONSUMER_SECRET=your_twitter_consumer_secret
   ACCESS_TOKEN=your_twitter_access_token
   ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
   SERVER_PORT=8080
   ```

   Replace the placeholders with your actual keys and tokens.

4. **Run the server:**

   ```bash
   uvicorn main:app --reload
   ```

   The server will start on `http://127.0.0.1:8080`.

## API Endpoints

- **POST `/x/api/posts/create`**: Create a new tweet.
  - **Parameters**:
    - `text` (required): The text content of the tweet.
    - `url` (optional): A URL to include as a reply to the tweet.
    - `image` (optional): An image file to attach to the tweet.
  - **Headers**:
    - `X-API-Key`: Your server API key.

## Logging

The application logs important events and errors to the console. Logs include timestamps, log levels, and messages.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.