# x

This project is part of the [content-maestro](https://github.com/think-root/content-maestro) repository. If you want Twitter integration and automatic publishing of posts there as well, you need to deploy this app.

## Description

This app provides a FastAPI-based server that integrates with the Twitter API to post tweets, optionally including media and URLs. It includes API key middleware for secure access and uses OAuth 1.0a for authentication with the Twitter API.

## Prerequisites

[requirements.txt](requirements.txt) includes all the dependencies needed to run this project.

## Setup

1. **Clone the repository:**

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
   MAX_TWEET_LENGTH=265
   ```

   Replace the placeholders with your actual data.

4. **Run the server:**

   ```bash
   uvicorn main:app --reload
   ```

   The server will start on `http://127.0.0.1:8080`.

## API

All endpoints require the `X-API-Key` header for authentication.

### Authentication

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `X-API-Key` | string | Yes | Your server API key from `.env` |

**Error Response (401 Unauthorized):**

```json
{
  "detail": "Invalid or missing API key"
}
```

---

### POST `/x/api/posts/create`

Creates a new tweet. Supports text, optional image attachment, and optional URL reply. Long texts are automatically split into a thread.

#### Request

**Content-Type:** `multipart/form-data`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | The text content of the tweet. If exceeds `MAX_TWEET_LENGTH`, will be split into a thread |
| `url` | string | No | A URL to include as a final reply to the tweet/thread |
| `image` | file | No | An image file to attach to the first tweet |

#### Examples

**Simple tweet:**

```bash
curl -X POST "http://localhost:8080/x/api/posts/create" \
  -H "X-API-Key: your_api_key" \
  -F "text=Hello, World!"
```

**Tweet with image:**

```bash
curl -X POST "http://localhost:8080/x/api/posts/create" \
  -H "X-API-Key: your_api_key" \
  -F "text=Check out this image!" \
  -F "image=@/path/to/image.jpg"
```

**Tweet with URL reply:**

```bash
curl -X POST "http://localhost:8080/x/api/posts/create" \
  -H "X-API-Key: your_api_key" \
  -F "text=Interesting article about AI" \
  -F "url=https://example.com/article"
```

**Full request (text + image + URL):**

```bash
curl -X POST "http://localhost:8080/x/api/posts/create" \
  -H "X-API-Key: your_api_key" \
  -F "text=Check out this amazing article!" \
  -F "url=https://example.com/article" \
  -F "image=@/path/to/image.jpg"
```

#### Response

**Success (200 OK):**

```json
{
  "tweets": [
    {
      "data": {
        "id": "1234567890123456789",
        "text": "Hello, World!"
      }
    }
  ]
}
```

**Success with thread (long text split into multiple tweets):**

```json
{
  "tweets": [
    {
      "data": {
        "id": "1234567890123456789",
        "text": "🧵 0/2 First part of the long text..."
      }
    },
    {
      "data": {
        "id": "1234567890123456790",
        "text": "🧵 1/2 Second part of the text..."
      }
    },
    {
      "data": {
        "id": "1234567890123456791",
        "text": "🧵 2/2 Final part of the text..."
      }
    }
  ]
}
```

**Error:**

```json
{
  "error": "Error message describing what went wrong"
}
```

---

### POST `/x/api/test/posts/create`

Creates a test tweet with the text "test". Used for verifying API connectivity and authentication.

#### Request

No parameters required.

```bash
curl -X POST "http://localhost:8080/x/api/test/posts/create" \
  -H "X-API-Key: your_api_key"
```

#### Response

**Success (200 OK):**

```json
{
  "tweets": [
    {
      "data": {
        "id": "1234567890123456789",
        "text": "test"
      }
    }
  ]
}
```

---

### Thread Behavior

When the tweet text exceeds `MAX_TWEET_LENGTH` (default: 265 characters), the API automatically:

1. Splits the text into multiple parts at word boundaries
2. Adds thread counters (e.g., `🧵 0/2`, `🧵 1/2`, `🧵 2/2`)
3. Posts each part as a reply to the previous tweet
4. Attaches the image (if provided) only to the first tweet
5. Adds the URL (if provided) as the final reply in the thread

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.