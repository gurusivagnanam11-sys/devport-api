# DevPort — API Management Platform

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-async%20tasks-37814A?logo=celery&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

DevPort is a production-grade API Management Platform built with FastAPI, inspired by
Kong, AWS API Gateway, and the Stripe Developer Platform. It sits in front of any
backend API and provides authentication, authorization, rate limiting, usage
analytics, and webhook notifications — the infrastructure a company needs before it
can safely expose an API to external developers.

This project was built as a structured, from-scratch learning exercise covering the
full backend engineering lifecycle: data modeling, auth, multi-tenant authorization,
distributed rate limiting, background processing, security hardening, automated
testing, and containerized deployment.

---

## About / Why This Project

Most portfolio projects are CRUD apps — a todo list, a blog — which mainly test
whether you can wire a database to a UI. I wanted to build something that forced me
to think like a backend infrastructure engineer instead: authentication and
authorization as separate concerns, multi-tenant data isolation, distributed rate
limiting under real concurrency, async background processing with proper retry
semantics, and security review as its own deliberate practice.

I built this **module by module**, deliberately understanding the reasoning behind
every decision (why bcrypt vs SHA-256, why atomic Lua scripting, why fail-open vs
fail-closed) rather than copying a tutorial — so I can explain the *why* behind every
piece, not just what the code does.

---

## Why this exists

A raw, unprotected API endpoint —

```
GET /weather
```

— has no authentication, no rate limiting, no usage tracking, and no way to manage
who can call it or how often. DevPort solves this by acting as a gateway: every
request passes through authentication, workspace/role checks, rate limiting, and
logging before reaching the protected API underneath.

```
Client
  │
  ▼
DevPort Gateway
  ├── JWT / API Key validation
  ├── Workspace + RBAC checks
  ├── Redis rate limiter (atomic, Lua-scripted)
  ├── Usage logging
  └── Webhook dispatch (async, via Celery)
  │
  ▼
Protected API (e.g. /v1/weather)
```

---

## Features

- **Authentication** — registration, login, JWT access + refresh tokens, bcrypt
  password hashing, protected routes
- **Workspace Management** — multi-user workspaces (teams/companies), invite/remove
  members
- **RBAC** — centralized Admin/Member permission matrix, enforced via FastAPI
  dependency injection
- **Multi-Tenancy** — every tenant-owned resource is scoped by `workspace_id`;
  IDOR-safe (non-members get 404, not 403, preventing resource enumeration)
- **API Key Management** — CSPRNG-generated keys, SHA-256 hashed at rest, key
  prefixes for identification, rotate/revoke support
- **Rate Limiting** — Redis + Lua scripting for atomic, race-condition-free request
  counting; tiered plans (Free / Pro / Enterprise); `429` + `Retry-After` responses
- **Usage Analytics** — per-workspace request logs, top endpoints, average latency,
  daily usage trends, aggregated in SQL
- **Webhooks** — HMAC-signed event delivery, exponential backoff retries, dead
  letter queue for permanently failed deliveries
- **Background Processing** — Celery workers + Beat scheduler for async webhook
  delivery and periodic cleanup jobs
- **Security Hardening** — fail-fast secret validation, constant-time comparisons,
  no default secrets, generic error responses, explicit CORS policy
- **Testing** — pytest unit + integration tests, isolated in-memory test database,
  dependency-injected overrides
- **Deployment** — Docker, Docker Compose (API + worker + beat + Postgres + Redis),
  GitHub Actions CI, Railway-ready

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI, Pydantic v2 |
| Database | PostgreSQL, SQLAlchemy 2.0, Alembic |
| Auth | python-jose (JWT), passlib + bcrypt |
| Caching / Rate Limiting | Redis, Lua scripting |
| Background Jobs | Celery, Redis (broker) |
| Testing | pytest, httpx, SQLite (test DB) |
| Deployment | Docker, Docker Compose, GitHub Actions, Railway |

---

## Project Structure

```
devport-api/
├── app/
│   ├── main.py
│   ├── core/              # config, database, redis client, celery app — shared infra
│   ├── auth/               # register, login, JWT, protected-route dependency
│   ├── workspaces/          # workspace CRUD, membership, RBAC permission matrix
│   ├── api_keys/            # API key generation, hashing, rotate/revoke
│   ├── rate_limit/          # Redis + Lua atomic rate limiter, plan tiers
│   ├── analytics/           # usage logging + SQL aggregation
│   ├── webhooks/            # HMAC signing, Celery delivery tasks, dead letter queue
│   └── gateway/             # sample protected endpoint (/v1/weather)
├── alembic/                 # database migrations
├── tests/                   # pytest unit + integration tests
├── .github/workflows/       # CI pipeline
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

Structured as **vertical slices** (one folder per feature, not per technical layer) —
each feature folder contains its own `models.py`, `schemas.py`, `service.py`, and
`router.py`, so working on any one feature means opening one folder, not four.

---

## Getting Started

### Prerequisites
- Python 3.12+
- Docker & Docker Compose

### Run with Docker Compose (recommended)

```bash
git clone git@github.com:gurusivagnanam11-sys/devport-api.git
cd devport-api
cp .env.docker.example .env.docker   # fill in your own JWT_SECRET_KEY
docker compose up --build
```

Run migrations once the containers are up:

```bash
docker compose exec api alembic upgrade head
```

API available at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

### Run locally (without Docker)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set DATABASE_URL, JWT_SECRET_KEY, REDIS_URL

alembic upgrade head
uvicorn app.main:app --reload
```

Start the background workers in separate terminals:

```bash
celery -A app.core.celery_app worker --loglevel=info
celery -A app.core.celery_app beat --loglevel=info
```

### Run tests

```bash
pytest -v
```

---

## Example Flow

```bash
# 1. Register
POST /auth/register  {"email": "you@example.com", "password": "..."}

# 2. Login
POST /auth/login  {"email": "you@example.com", "password": "..."}
# → returns access_token + refresh_token

# 3. Create a workspace
POST /workspaces/  (Authorization: Bearer <access_token>)
  {"name": "My Company"}

# 4. Generate an API key
POST /workspaces/{id}/api-keys/  {"name": "Production Key"}
# → raw_key shown ONCE — save it now

# 5. Call the protected sample API
GET /v1/weather
Header: x-api-key: <raw_key>
```

---

## Design Notes Worth Knowing

- **JWT vs API Keys** — JWTs authenticate logged-in human users (short-lived access
  + longer-lived refresh tokens). API keys authenticate machine-to-machine calls to
  the protected APIs and are long-lived until explicitly rotated/revoked.
- **bcrypt vs SHA-256** — passwords are hashed with bcrypt (deliberately slow, resists
  brute-forcing guessable secrets). API keys are hashed with SHA-256 (fast, because
  they're already high-entropy CSPRNG-generated values checked on every request).
- **Fail-open rate limiting** — if Redis is unreachable, requests are allowed through
  rather than blocking all traffic; a documented, deliberate tradeoff (see
  `app/rate_limit/limiter.py`).
- **404, not 403, for non-members** — accessing a workspace you don't belong to
  returns 404 regardless of whether the workspace exists, preventing resource
  enumeration (IDOR prevention).

---

## License

MIT
