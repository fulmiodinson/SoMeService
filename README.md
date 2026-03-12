# SoMeService

FastAPI application for storing social media data from YouTube, Instagram etc.

## Features

- Async FastAPI application backed by PostgreSQL
- CRUD endpoints for `SoMeProvider`, `SoMeAccount`, `SoMeAccountThumbnail`, `SoMeAccountItem`
- Image upload/storage for account thumbnails (served as static files)
- JWT authentication via a self-hosted Keycloak realm
- Database migrations managed with Alembic + SQLAlchemy 2 (async)
- Docker support: multi-stage `Dockerfile` (development + production) and a `docker-compose.yml` for the development setup

## Project layout

```
app/
  auth/           Keycloak JWT validation
  crud/           Async CRUD helpers (generic base + per-model)
  models/         SQLAlchemy ORM models
  routers/        FastAPI routers (one per resource)
  schemas/        Pydantic request/response schemas
  config.py       Pydantic-Settings configuration
  database.py     Async engine & session factory
  main.py         FastAPI application factory
alembic/          Alembic migration environment
  versions/       Migration scripts
Dockerfile        Multi-stage build (development / production targets)
docker-compose.yml Development stack (app + PostgreSQL)
```

## Configuration

Copy `.env.example` to `.env` and fill in the values:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Async PostgreSQL URL (`postgresql+asyncpg://…`) |
| `KEYCLOAK_URL` | Base URL of your Keycloak instance, e.g. `https://keycloak.example.com` |
| `KEYCLOAK_REALM` | Realm name |
| `KEYCLOAK_CLIENT_ID` | Client ID used for audience validation (leave empty to skip) |
| `MEDIA_ROOT` | Filesystem path where uploaded images are stored (default `/app/media`) |
| `MEDIA_URL` | URL prefix for serving media files (default `/media/`) |
| `DEBUG` | Enable SQLAlchemy query logging (`false` by default) |

## Running with Docker Compose (development)

```bash
cp .env.example .env
# edit .env with your Keycloak settings

docker compose up --build
```

The API is available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

## Running database migrations

```bash
# inside the running app container
docker compose exec app alembic upgrade head

# or locally (with DATABASE_URL pointing at the DB)
alembic upgrade head
```

## API overview

All endpoints require a valid Keycloak Bearer token:

```
Authorization: Bearer <access_token>
```

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/providers/` | List providers |
| POST | `/api/v1/providers/` | Create provider |
| GET | `/api/v1/providers/{id}` | Get provider |
| PATCH | `/api/v1/providers/{id}` | Update provider |
| DELETE | `/api/v1/providers/{id}` | Delete provider |
| GET | `/api/v1/accounts/` | List accounts (filter by `?provider_id=`) |
| POST | `/api/v1/accounts/` | Create account |
| GET | `/api/v1/accounts/{id}` | Get account |
| PATCH | `/api/v1/accounts/{id}` | Update account |
| DELETE | `/api/v1/accounts/{id}` | Delete account |
| GET | `/api/v1/thumbnails/` | List thumbnails (filter by `?account_id=`) |
| POST | `/api/v1/thumbnails/` | Create thumbnail metadata |
| GET | `/api/v1/thumbnails/{id}` | Get thumbnail |
| PATCH | `/api/v1/thumbnails/{id}` | Update thumbnail metadata |
| DELETE | `/api/v1/thumbnails/{id}` | Delete thumbnail |
| POST | `/api/v1/thumbnails/{id}/image` | Upload/replace image file |
| GET | `/api/v1/items/` | List items (filter by `?account_id=`, `?type=`) |
| POST | `/api/v1/items/` | Create item |
| GET | `/api/v1/items/{id}` | Get item |
| PATCH | `/api/v1/items/{id}` | Update item |
| DELETE | `/api/v1/items/{id}` | Delete item |
| GET | `/health` | Health check |

## Production deployment

Build the production image:

```bash
docker build --target production -t someservice:latest .
```

Run it (pass environment variables via `-e` or an env file):

```bash
docker run --env-file .env -p 8000:8000 someservice:latest
```
