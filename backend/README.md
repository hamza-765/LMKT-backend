# LMKT Landing Page Backend

This repository contains the backend-only API for the LMKT landing page. It is built with FastAPI and is designed to be consumed by a separate frontend application.

## What this backend does

The backend provides three main features for the landing page:

1. LMKT chatbot API
   - Domain-restricted question answering
   - Uses only the provided LMKT knowledge files
   - Refuses out-of-domain and prompt-injection requests safely

2. ROI calculator API
   - Deterministic backend-only business calculation
   - No AI involved
   - Easy to change formulas later without touching the frontend

3. Lead submission API
   - Stores contact form submissions in MongoDB
   - Returns a lead identifier (a string MongoDB ObjectId) after successful save
   - Includes a read endpoint for testing and inspection

## Tech stack

- Python 3.12+
- FastAPI
- Pydantic
- MongoDB (via Motor, the async driver)
- Google Gemini API
- Environment variables with `.env`
- OpenAPI / Swagger
- Modular backend architecture

## Frontend integration summary

The frontend should call this backend through a single base URL such as:

```text
http://127.0.0.1:8000
```

All endpoints are REST JSON APIs. The frontend should send `Content-Type: application/json` for POST requests.

**Nothing changes on the frontend side for this backend swap.** The API paths, request bodies, and response shapes are the same as before, with one exception: `lead_id` in the lead submission response is now a **string** (a MongoDB ObjectId, e.g. `"66f1a2b3c4d5e6f7a8b9c0d1"`) instead of an integer. If the frontend was treating `lead_id` as a number anywhere (parsing it, doing math on it), that needs to change to treat it as an opaque string ID.

## Project structure

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── middleware.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── services/
├── knowledge/
│   ├── knowledge_base.json
│   └── system_prompt.txt
├── requirements.txt
├── README.md
└── .env.example
```

## Local setup

1. Open a terminal inside the backend folder.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the environment template:

```bash
copy .env.example .env
```

5. Fill in the required values in `.env` — most importantly `MONGODB_URI` (see below).

6. Start the app:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The app pings MongoDB on startup. If the connection fails, the server will refuse to start and print a connection error instead of starting silently broken — that's expected behavior, not a bug. See the "MongoDB setup" section below.

## Environment variables

The backend expects these settings in `.env`:

```env
APP_NAME=LMKT Landing Page Backend
ENVIRONMENT=development
DEBUG=false
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=lmkt_db
GEMINI_API_KEY=your_gemini_api_key_here
LOG_LEVEL=INFO
MAX_MESSAGE_LENGTH=500
```

### Notes

- `GEMINI_API_KEY` is required only when the chatbot is actually calling Gemini.
- `MONGODB_URI` can point at a local MongoDB instance (`mongodb://localhost:27017`) or a cloud cluster (MongoDB Atlas `mongodb+srv://...` string). No code changes are needed either way.
- After editing `.env`, you must fully stop and restart `uvicorn` — `--reload` only watches `.py` files, not `.env`, so it will not pick up env var changes on its own.
- CORS is enabled for frontend origins declared in `CORS_ORIGINS`.

## MongoDB setup

This backend needs a reachable MongoDB database — either:

- **Local**: install MongoDB Community Server and run it on the default port, then leave `MONGODB_URI=mongodb://localhost:27017` in `.env`.
- **Cloud (MongoDB Atlas)**: create a free cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas), create a database user, allow-list your IP under Network Access, and copy the connection string into `MONGODB_URI`.

Collections and databases are created automatically the first time a document is inserted — there is no manual schema setup or migration step. The `leads` collection lives inside the database named by `MONGODB_DB_NAME` (`lmkt_db` by default).

## API documentation

After starting the backend, the frontend developer can inspect the API contract here:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## API reference

### 1. Health check

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

### 2. Chatbot

```http
POST /api/chat
```

Request body:

```json
{
  "message": "Tell me about LMKT GIS solutions."
}
```

Success response:

```json
{
  "reply": "...",
  "success": true,
  "timestamp": "2026-08-01T12:00:00+00:00"
}
```

Important behavior:

- The chatbot is restricted to LMKT-related questions only.
- It must answer only from the provided knowledge base.
- If the answer is unavailable, it returns a safe fallback response.
- Out-of-domain or prompt-injection requests are refused politely.

### 3. ROI calculator

```http
POST /api/roi-calculator
```

Request body:

```json
{
  "sector": "Energy",
  "organization_size": "Large"
}
```

Example response:

```json
{
  "estimated_roi": 38,
  "annual_savings": 150000,
  "utility_efficiency": 27,
  "implementation_time": "6 months"
}
```

### 4. Lead submission

```http
POST /api/leads
```

Request body:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "company": "Example Corp",
  "sector": "Energy",
  "message": "Interested in GIS solutions"
}
```

Success response:

```json
{
  "success": true,
  "lead_id": "66f1a2b3c4d5e6f7a8b9c0d1"
}
```

> `lead_id` is a string (MongoDB ObjectId), not a number. Treat it as an opaque identifier — don't parse it as an integer.

### 5. Lead listing

```http
GET /api/leads
```

This endpoint is mainly for local testing and verification. It returns all saved leads, each with a string `id` field.

## Chatbot safety rules for frontend awareness

The frontend should understand that the chatbot behaves like a strict LMKT assistant. It will:

- answer only LMKT-domain questions
- never invent facts or statistics
- never answer unrelated topics
- return the fallback message when verified information is missing

## Database

The database is MongoDB, accessed asynchronously via Motor. The `leads` collection stores documents shaped like:

- `_id` (ObjectId, returned to clients as a string `id`)
- `name`
- `email`
- `phone`
- `company`
- `sector`
- `message`
- `created_at`

Because MongoDB is schema-flexible, adding new fields to leads in the future does not require a migration step.

## Logging and error behavior

The backend logs:

- incoming requests
- validation issues
- Gemini failures
- database errors
- unexpected exceptions

The API returns standard HTTP statuses such as:

- 400 for bad input
- 404 for missing routes/resources
- 422 for validation failures
- 429 for rate limiting scenarios if used later
- 500 for internal server errors

## Notes for the frontend developer

- This repo is backend only. No HTML, CSS, or UI code is included.
- Frontend should integrate through the API only.
- Use the Swagger docs while developing so the payloads and responses stay consistent.
- The chatbot is not a general-purpose AI assistant. It is intentionally limited to LMKT and enterprise solution knowledge.
- If the frontend wants to show the chatbot fallback, it should display the response returned by the API directly.
- The only breaking change from the previous version of this API is that `lead_id` / lead `id` values are now strings instead of numbers — everything else (URLs, request bodies, other response fields) is unchanged.

## Recommended development flow

1. Set `MONGODB_URI` in `.env` (local or Atlas) and confirm the server starts without a connection error.
2. Run backend locally.
3. Open the Swagger docs.
4. Confirm the frontend can call all three APIs.
5. Use the lead endpoint for form submission testing, and check MongoDB Atlas (or `mongosh`/Compass locally) to confirm documents are landing in the `leads` collection.
6. Keep the UI integration simple and JSON-driven.

## Testing

A small automated API test suite is included in the backend to verify the main endpoints. It requires a reachable MongoDB instance (set via `MONGODB_URI`) for the lead-related test to pass.

Run:

```bash
pytest
```

## Final note

This backend is built to be clean, modular, and easy to extend. The frontend team can consume it as a standard JSON API without needing to understand the internal implementation details.

## Vercel deployment note

For Vercel deploys, the backend connects to MongoDB Atlas (or any managed MongoDB) over the network rather than relying on a local file, which fits Vercel's stateless/ephemeral serverless environment naturally — there is no `/tmp` workaround needed as there was with SQLite.

Important deployment guidance:

- Vercel serverless instances are stateless and ephemeral, but MongoDB Atlas is an external, persistent, managed service, so this is not a concern for data durability.
- Set `MONGODB_URI` and `MONGODB_DB_NAME` as environment variables in the Vercel project settings (not committed to the repo).
- Make sure MongoDB Atlas Network Access allows connections from Vercel (Atlas's "Allow access from anywhere" `0.0.0.0/0` option is the simplest approach for serverless platforms with dynamic IPs).
