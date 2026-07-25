# DevPort

DevPort is a FastAPI-based API management platform that acts as an API gateway (similar to Kong, AWS API Gateway, or Stripe's developer platform). It sits in front of backend APIs to provide essential infrastructure such as authentication, rate limiting, and usage analytics.

## About / Why This Project

This project was built module-by-module to demonstrate real backend infrastructure concepts rather than a simple CRUD application. It showcases practical implementations of authentication, role-based access control (RBAC), multi-tenancy, distributed rate limiting, asynchronous processing, security review, testing, and containerized deployment.

## Features

- **Authentication**: User registration, login, JWT issuance, and refresh mechanisms.
- **Workspaces**: Multi-tenant workspace management with CRUD operations, membership management, and an RBAC permission matrix.
- **API Keys**: Secure API key generation, cryptographic hashing, and rotate/revoke capabilities.
- **Rate Limiting**: Distributed atomic rate limiting using Redis and Lua scripts.
- **Analytics**: API usage logging and SQL-based aggregation.
- **Webhooks**: Event delivery with HMAC signing, asynchronous processing via Celery, and a dead letter queue.
- **Gateway**: A sample protected gateway endpoint to demonstrate API request routing and validation.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** (0.139.0) | High-performance web framework for the API |
| **SQLAlchemy** (2.0.51) | ORM for database interactions |
| **Alembic** (1.18.5) | Database migration tool |
| **Pydantic** (2.13.4) | Data validation and settings management |
| **Celery** (5.6.3) | Asynchronous task queue for webhook delivery |
| **Redis** | In-memory store for rate limiting and Celery message broker |
| **PostgreSQL** | Primary relational database |
| **Docker** | Containerized deployment and orchestration |
| **React / Vite** | Frontend developer dashboard |

## Project Structure

```text
alembic/
app/
  analytics/
  api_keys/
  auth/
  core/
  gateway/
  rate_limit/
  webhooks/
  workspaces/
frontend/
tests/
```

## Getting Started

### Using Docker Compose

1. Build and start the containers:
   ```bash
   docker compose up --build
   ```
2. Apply database migrations:
   ```bash
   docker compose exec api alembic upgrade head
   ```

### Local Setup (Virtual Environment)

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (copy `.env.example` to `.env` and fill it out):
   ```bash
   cp .env.example .env
   ```
4. Run database migrations:
   ```bash
   alembic upgrade head
   ```
5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Running the Frontend

The project includes a React dashboard. To run it locally:

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server (make sure your `API_BASE` environment variable is configured properly):
   ```bash
   npm run dev
   ```

### Running Tests

The project has a comprehensive test suite. To run the tests, execute:

```bash
pytest -v
```

Currently, **24 tests** are passing across the auth, security, api_keys, and workspaces modules.

## Verified Working

The following core modules have been manually verified end-to-end against a live running instance (FastAPI + PostgreSQL + Redis + Celery):

- **Authentication**: Registration, login, JWT validation, and token refreshing.
- **Workspace Management**: Creation, listing, updating, and deletion (including IDOR prevention).
- **RBAC**: Enforcement of role-based permissions (admin vs. member).
- **API Key Management**: Creation and raw-key validation against a protected sample endpoint.
- **Rate Limiting**: Atomic, distributed 100 requests/day boundary enforced correctly using Redis Lua scripts.
- **Usage Analytics**: Correct logging of usage counts, appropriately excluding rate-limited requests.
- **Webhooks & Background Processing**: Event dispatch, HMAC signing, and asynchronous delivery via Celery to real public endpoints.
